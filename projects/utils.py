import re
from pprint import pprint

from django.db.models import Q, QuerySet

from projects.models import Projects, KindOfOfInfluences, ViolatorLvls, Bdus, ObjectOfInfluences, Capecs


def create_word(project: Projects):
    pass


def genereate_neg_con_table(project: Projects):
    table = {'column_name': ['Вид риска (ущерба)', 'Возможные негативные последствия']}
    neg_cons = project.negative_consequences.all().order_by('type')
    for neg_con in neg_cons:
        if neg_con.type in table:
            table[neg_con.type].append(neg_con.name)
        else:
            table[neg_con.type] = [neg_con.name]
    pprint(table)

    # todo создать excel файл и вернуть его
    return table


def generate_obj_inf_table(project: Projects):
    table = {'column_name': ['Негативные последствия', 'Объекты воздействия', 'Виды воздействия']}
    neg_cons = project.negative_consequences.all()
    for neg_con in neg_cons:
        if 'физическому' in neg_con.type:
            lvl = 'У1'
        elif 'юридическому' in neg_con.type:
            lvl = 'У2'
        else:
            lvl = 'У3'
        objs = neg_con.object_of_influence.all()
        for obj in objs:
            if obj in project.object_inf.all():
                kind = KindOfOfInfluences.objects.get(object_of_inf=obj, neg_cons=neg_con).kind_of_inf
                if f'{neg_con.name} ({lvl})' in table:
                    temp = table[f'{neg_con.name} ({lvl})']
                    table.update({f'{neg_con.name} ({lvl})': temp | {obj.name: kind}})
                else:
                    table[f'{neg_con.name} ({lvl})'] = {obj.name: kind}
        if f'{neg_con.name} ({lvl})' not in table:
            table[f'{neg_con.name} ({lvl})'] = {
                'нет потенциальных объектов воздействия': 'воздействие отсутствует'}

            # todo создать excel файл и вернуть его
    pprint(table)
    return table


def generate_violators_type_table(project: Projects):
    # вид нарушителя(название), тип нарушителя (внеш, внут), Возможные цели (мотивация) реализации угроз безопасности информации
    table = {'column_name':
                 ['Вид нарушителя',
                  'Тип нарушителя',
                  'Возможные цели (мотивация) реализации угроз безопасности информации']
             }
    violators = project.violators.all()
    for violator in violators:
        if violator.type == 1:
            types = ['внутренний']
        elif violator.type == 2:
            types = ['внешний']
        else:
            types = ['внутренний', 'внешний']
        for type in types:
            if violator.name in table:
                temp = table[violator.name]
                table.update({violator.name: temp | {type: violator.motives}})
            else:
                table[violator.name] = {type: violator.motives}
    # todo создать excel файл и вернуть его
    pprint(table)
    return table


def generate_violators_potential_table(project: Projects):
    # Уровень возможностей, вид нарушителя(название), потенциал нарушителя
    table = {'column_name':
                 ['Уровень возможностей',
                  'Вид нарушителя',
                  'Потенциал нарушителя']
             }
    vlvls = ViolatorLvls.objects.all().order_by('lvl')
    for lvl in vlvls:
        violators = lvl.violators.all()
        for violator in violators:
            if violator.potential == 1:
                potential = 'низкий'
            elif violator.type == 2:
                potential = 'средний'
            else:
                potential = 'высокий'
            if violator in project.violators.all():
                if lvl.name in table:
                    temp = table[lvl.name]
                    table.update({lvl.name: temp | {violator.name: potential}})
                else:
                    table[lvl.name] = {violator.name: potential}
    # todo создать excel файл и вернуть его
    pprint(table)
    return table


def generate_bdu_table(project: Projects):
    '''
    эта таблица не уместится в обычном варианте ворда,
    лист нужно будет развернуть горизонтально что бы она поместилась хоть как-то
    и придётся уменьшить шрифт для неё
    :param project:
    :return:
    '''
    # номер угрозы, название, уязвимость(опционально), вектор капек, нег пос, объект воздействия, нарушитель, сценарий реализации
    table = {'column_name':
                 ['Номер угрозы',
                  'Название',
                  'Уязвимость',  # поле будет пустое
                  'Вектор Капек',
                  'Негативное последствие',
                  'Объект воздействия',
                  'ТН',
                  'Сценарий реализации',  # поле будет пустое
                  ]
             }
    correct_obj_list = project.object_inf.all()

    bdus: QuerySet[Bdus] = form_bdus_list_for(project).order_by('id')
    # Bdus.objects.all()
    bdus.all()
    for bdu in bdus:
        capecs: QuerySet[Capecs] = bdu.capecs.all()
        for capec in capecs:
            number = f"УБИ.{bdu.id}"

            # формирование цепочки капек от родителя до текущего
            cpc = form_capec_vector_for(capec)

            # нег взять дискрипшион  обрезать строку "Угроза заключается в возможности"
            # включительно убрать _x000D и всё что после
            neg_con = bdu.description.replace("Угроза заключается в возможности", '')
            neg_con = neg_con.replace(r'_x000D*', '')
            neg_con = re.sub('(_x000D).*', '', neg_con, re.DOTALL).split('\n', 1)[0]

            vulnerability = 'ручное заполнение'
            obj_of_infs = bdu.bdus.all()
            violator = bdu.violator
            scenario = 'сценарий реализации - функция в разработке'
            violator_dict = {violator: scenario}
            neg_con_dict = {}
            for obj_of_inf in obj_of_infs:
                if obj_of_inf in correct_obj_list:
                    obj_of_inf = obj_of_inf.name
                else:
                    obj_of_inf = 'нет актуальных объектов'

                if neg_con in neg_con_dict:
                    temp = neg_con_dict[neg_con]
                    neg_con_dict.update({neg_con: temp | {obj_of_inf: violator_dict}})
                else:
                    neg_con_dict[neg_con] = {obj_of_inf: violator_dict}
            vulnerability_dict = {vulnerability: neg_con_dict}
            cpc_dict = {cpc: vulnerability_dict}
            if number in table:
                temp = table[number]
                table.update({number: temp | {bdu.name: cpc_dict}})
            else:
                table[number] = {bdu.name: cpc_dict}

    # todo создать excel файл и вернуть его

    print(table)
    return table


def form_capec_vector_for(capec: Capecs) -> str:
    cpc: list[str] = []
    while True:
        cpc.append(f'CAPEC-{capec.id}: {capec.name}')
        # todo должно быть is None, но база данных хранит не все капеки, поэтому алгоритм кидает ошибки
        if (capec.parent_id is not None):
            break
        capec = Capecs.objects.get(id=capec.parent_id)

    result = '\n'.join(cpc)
    return result


def form_bdus_list_for(project: Projects) -> QuerySet[Bdus]:
    # функция которая подвязывает к проекту актуальные бдухи
    project = Projects.objects.get(id=3)
    # фильтрация по объектам
    objects = ObjectOfInfluences.objects.filter(name__in=project.object_inf.values_list('name', flat=True))
    bdu = Bdus.objects.none()
    for object in objects:
        a = object.bdus.all()
        bdu = bdu | a
    # при фильтрации потегам селект none or true/false
    bdu = bdu.distinct()
    bdu = bdu.filter(Q(is_wireless=project.is_wireless) | Q(is_wireless=None))
    bdu = bdu.filter(Q(is_grid=project.is_grid) | Q(is_grid=None))
    bdu = bdu.filter(Q(is_virtual=project.is_virtual) | Q(is_virtual=None))
    bdu = bdu.filter(Q(is_cloud=project.is_cloud) | Q(is_cloud=None)).order_by('id')

    # фильтрация по нарушителям
    # todo я переделал функцию, возможно она сломалась, нужно затестить
    violators = project.get_violator_lvl_names()
    bdu = bdu.filter(violator__in=violators)

    return bdu
