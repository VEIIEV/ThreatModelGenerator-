from pprint import pprint

from django.db.models import Q, QuerySet

from projects.models import Projects, KindOfOfInfluences, ViolatorLvls, Bdus, ObjectOfInfluences


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
    # todo при составление таблицы, если не выбран объект воздействия в тесте, указывать не актуальность
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

    bdus = form_bdus_list_for(project)

    # todo создать excel файл и вернуть его

    pass


def form_bdus_list_for(project: Projects):
    # функция которая подвязывает к проекту актуальные бдухи
    project = Projects.objects.get(id = 3)
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
    violators = set()
    for violator in project.violators.all():
        violators.add(violator.lvl.name)
    bdu = bdu.filter(violator__in=violators)

    pprint(bdu)
    return bdu
