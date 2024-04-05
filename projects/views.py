import re
from datetime import date
from django.http import FileResponse
from django.shortcuts import render
import os
import pandas as pd
import xlwt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest, QueryDict
from django.shortcuts import render
from django.views import View
from docx import Document
from docx.table import Table

from profils.models import User
from .models import Projects, Capecs, Bdus, RPersons, NegativeConsequences, ObjectOfInfluences, Violators, ViolatorLvls
from .utils import create_word, genereate_neg_con_table, generate_obj_inf_table, generate_violators_type_table, \
    generate_violators_potential_table, form_bdus_list_for, generate_bdu_table


# todo накатить фронт,


class CreateProject(View):
    system_type = {"GYS": "Государственная информационная система",
                   "ISP": "Информационная система пресональных данных",
                   "KII": "Объект критической информакционной инфраструктуры"}

    def get(self, request: HttpRequest):
        stage = request.GET.get('stage')
        project_id = request.GET.get('id')
        project = None

        if project_id is not None:
            project = Projects.objects.get(id=project_id)
        match stage:
            case None:
                project = Projects.objects.create(user=request.user)
                project.save()
                return render(request, '../templates/projects/create_project_1.html', context={'project': project})
            case '1':
                return render(request, '../templates/projects/create_project_1.html', context={'project': project})
            case '2':
                return render(request, '../templates/projects/create_project_2.html',
                              context={'project': project,
                                       'system_type': self.system_type})
            case '3':
                return render(request, '../templates/projects/create_project_3.html', context={'project': project})
            case '4':
                ncs = project.negative_consequences.values_list('id', flat=True)
                return render(request, '../templates/projects/create_project_4.html',
                              context={'project': project,
                                       'negative_consequences': NegativeConsequences.objects.all(),
                                       'ncs': ncs})
            case '5':
                ob_ids = project.object_inf.values_list('id', flat=True)

                proj_vars = vars(project)
                add_options = {}
                for key, value in proj_vars.items():
                    if 'is_' in key:
                        add_options[key] = value

                return render(request, '../templates/projects/create_project_5.html',
                              context={'project': project,
                                       'objs': ObjectOfInfluences.objects.all(),
                                       'ob_ids': ob_ids,
                                       'add_options': add_options})
            case '6':

                v_lvl_names = project.get_violator_lvl_names()
                return render(request, '../templates/projects/create_project_6.html',
                              context={'project': project,
                                       'violators': ViolatorLvls.objects.all(),
                                       'v_lvl_names': v_lvl_names})
            case '7':

                # todo добавить кнопку для выгрузки каждой таблице отдельно как excel
                # todo добавить кнопку для выгрузки всего ворд документа
                return render(request, '../templates/projects/create_project_7.html', context={'project': project})

    def post(self, request: HttpRequest):

        stage = request.GET.get('stage')
        # todo разобраться с этим куском говна
        # request_get = request.GET.copy()
        # request_get['stage'] = int(stage) + 1
        # request.GET = request_get
        project_id = int(request.GET.get('id'))
        project = Projects.objects.get(id=project_id)

        if (int(stage) < project.stage):
            project.roll_back_to_stage(stage)

        match stage:
            # todo в темплейте реализовать возможность создания нескольких ответственных лиц
            # todo не помечается не выбранные результаты
            case '1':
                r_person = RPersons.objects.create(name=request.POST['rperson_name'],
                                                   appointment=request.POST['appointment'],
                                                   projects=project)
                project.r_persons.add(r_person)
                project.name_project = request.POST['name_project']
                project.stage = 2
                project.save()
                return render(request, '../templates/projects/create_project_2.html', context={'project': project})
            case '2':
                project.type = request.POST['type']
                project.stage = 3
                project.save()
                return render(request, '../templates/projects/create_project_3.html',
                              context={'project': project,
                                       'system_type': self.system_type})
            case '3':
                project.system_lvl = request.POST['system_lvl']
                project.stage = 4
                project.save()
                return render(request, '../templates/projects/create_project_4.html',
                              context={'project': project,
                                       'negative_consequences': NegativeConsequences.objects.all()})
            case '4':
                data = QueryDict(request.body)
                for key in data.keys():
                    if key == 'csrfmiddlewaretoken':
                        continue
                    np_id = data.get(key)
                    neg_p = NegativeConsequences.objects.get(id=int(np_id))
                    project.negative_consequences.add(neg_p)
                    # project.save()
                project.stage = 5
                project.save()

                proj_vars = vars(project)
                add_options = {}
                for key, value in proj_vars.items():
                    if 'is_' in key:
                        add_options[key] = value

                return render(request, '../templates/projects/create_project_5.html',
                              context={'project': project,
                                       'objs': ObjectOfInfluences.objects.all(),
                                       'add_options': add_options})
                pass
            case '5':
                # TODO должно быть выбрано хотя бы 1 обязательное поле
                data = QueryDict(request.body)
                print(data)
                for key in data.keys():
                    if re.search("D_", key) is not None:
                        obj_id = data.get(key)
                        obj = ObjectOfInfluences.objects.get(id=int(obj_id))
                        project.object_inf.add(obj)
                project.is_grid = True if ("A_grid system" in data) else False
                project.is_virtual = True if ("A_virtual system" in data) else False
                project.is_wireless = True if ("A_wireless system" in data) else False
                project.is_cloud = True if ("A_cloud system" in data) else False
                project.stage = 6
                project.save()

                return render(request, '../templates/projects/create_project_6.html',
                              context={'project': project,
                                       'violators': ViolatorLvls.objects.all()})

            case '6':
                data = QueryDict(request.body)
                print(data)
                for key in data.keys():
                    if re.search("D_", key) is not None:
                        vio_lvl = data.get(key)
                        violators = ViolatorLvls.objects.get(lvl=vio_lvl).violators.all()
                        for violator in violators:
                            project.violators.add(violator)
                project.stage = 7
                project.save()

                return render(request, '../templates/projects/create_project_7.html', context={'project': project})
            case '7':
                # todo дело сделано, показываем итог и выгружаем док
                doc = create_word(project)

                pass


class ChooseSystemLvl(View):

    system_lvl_dict = {'1': [[1, 1], [1, 2], [1, 3], [2, 1]],
                       '2': [[2, 2], [2, 3], [3, 1]],
                       '3': [[3, 2], [3, 3]]}

    def get(self, request: HttpRequest):
        project_id = request.GET.get('id')
        project = Projects.objects.get(id=project_id)
        return render(request, f'../templates/projects/choose_lvl_{project.type}.html', context={'project': project})

    def post(self, request: HttpRequest):
        project_id = request.GET.get('id')
        project = Projects.objects.get(id=project_id)
        stage = request.GET.get('stage')
        if (int(stage) < project.stage):
            project.roll_back_to_stage(stage)
        match project.type:
            case 'KII':
                pass

            case 'GYS':
                signif_lvl = max(int(request.POST['confidentiality']),
                                 int(request.POST['integrity']),
                                 int(request.POST['accessibility']))
                scope = int(request.POST['scope'])
                for lvl, value in self.system_lvl_dict.items():
                    if [signif_lvl, scope] in value:
                        project.system_lvl = lvl
                        project.stage = 4
                        project.save()
                        break
                return render(request, '../templates/projects/create_project_4.html',
                              context={'project': project,
                                       'negative_consequences': NegativeConsequences.objects.all()})

            case 'ISP':
                pass


@login_required(login_url='profils:logun_users')
def Projects_list(request):
    paginate_by = 6
    users_project = Projects.objects.filter(user_id=request.user.id)
    paginator = Paginator(users_project, paginate_by)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {
        'projects': users_project,
        'page_obj': page_obj
    }
    return render(request, '../templates/projects/my_projects.html', context=data)


def Show_Projects(request, id):
    users_project = Projects.objects.get(id=id)
    data = {
        'project': users_project
    }
    return render(request, '../templates/projects/detail_project.html', data)


def Download_Project(request: HttpRequest):
    project = Projects.objects.get(id=request.GET.get('id'))
    neg_pos = genereate_neg_con_table(project)
    doc = Document('shablon_modeli_ugroz.docx')

    for paragraph in doc.paragraphs:
        if 'Модель угроз' in paragraph.text:
            paragraph.text = paragraph.text.replace('Модель угроз', 'Тест замены2')
    # автозаполнения даты
    table = doc.tables[0]
    current_date = str(date.today())
    table.cell(0, 1).text = current_date
    table2 = doc.tables[1]

    # заполнение таблицы нег.последствия
    for key in neg_pos:
        for elems in neg_pos[key]:  # тут мы перебираем список
            new_row = table2.add_row().cells
            new_row[0].text = key
            new_row[1].text = elems

    # удаляю повтор.значения в таблице
    row_count = len(table2.rows)
    col_count = len(table2.columns)
    listok = []
    for row in range(row_count):
        for col in range(col_count):
            if table2.cell(row, col).text in listok:
                table2.cell(row, col).text = ""
            else:
                listok.append((table2.cell(row, col).text))

    # скрещиваю пустые ячейки с пред идущимиЫ
    for row in range(row_count):
        if table2.cell(row, 0).text == '':
            table2.cell(row - 1, 0).merge(table2.cell(row, 0))

    # работа с таблицей №3   {         {     {       }        }          }
    objinftable = generate_obj_inf_table(project)
    table3 = doc.tables[2]
    for key in objinftable:
        for elem in objinftable[key]:
            # for key_to in objinftable[key][elem]:
            new_row = table3.add_row().cells
            new_row[0].text = key
            new_row[1].text = elem
            new_row[2].text = objinftable[key][elem]

    # работа с таблицей №4
    gen_vio = generate_violators_type_table(project)
    table4 = doc.tables[3]
    for key in gen_vio:
        for elem in gen_vio[key]:
            new_row = table4.add_row().cells
            new_row[0].text = str(key)
            new_row[1].text = str(elem)
            new_row[2].text = str(gen_vio[key][elem])
    # работа с таблицей №5
    gen_poten = generate_violators_potential_table(project)

    table5: Table = doc.tables[4]
    for key in gen_poten:
        for elem in gen_poten[key]:
            new_row = table5.add_row().cells
            new_row[0].text = key
            new_row[1].text = elem
            new_row[2].text = str(gen_poten[key][elem])

    row_count = len(table5.rows)
    col_count = len(table5.columns)
    listok = []
    for row in range(row_count):
        for col in range(col_count):
            if table5.cell(row, col).text in listok and table5.cell(row, col).text not in ['высокий', 'низкий',
                                                                                           'средний']:
                table5.cell(row, col).text = ""
            else:
                listok.append((table5.cell(row, col).text))

    for row in range(row_count):
        if table5.cell(row, 0).text == '':
            table5.cell(row - 1, 0).merge(table5.cell(row, 0))

    # таблица №6
    count = 0
    gen_bdu = generate_bdu_table(project)
    print('111111111111111111111111111111111111111111111111111')
    table6: Table = doc.tables[5]
    for number_ugroz in gen_bdu:
        print(number_ugroz)
        for name_ugroz in gen_bdu[number_ugroz]:
            for uyazvimost in gen_bdu[number_ugroz][name_ugroz]:
                for vectorCapec in gen_bdu[number_ugroz][name_ugroz][uyazvimost]:
                    for negativ in gen_bdu[number_ugroz][name_ugroz][uyazvimost][vectorCapec]:
                        for object in gen_bdu[number_ugroz][name_ugroz][uyazvimost][vectorCapec][negativ]:
                            for tn in gen_bdu[number_ugroz][name_ugroz][uyazvimost][vectorCapec][negativ][object]:
                                new_row = table6.add_row().cells
                                new_row[0].text = number_ugroz
                                new_row[1].text = name_ugroz
                                new_row[2].text = uyazvimost
                                new_row[3].text = vectorCapec
                                new_row[4].text = negativ
                                new_row[5].text = object
                                new_row[6].text = tn
                                new_row[7].text = \
                                    gen_bdu[number_ugroz][name_ugroz][uyazvimost][vectorCapec][negativ][object][tn]

    row_count = len(table6.rows)
    col_count = len(table6.columns)
    listok = []
    temp = None
    for row in range(row_count):
        if table6.cell(row, 0).text != temp:
            listok.clear()
            temp = table6.cell(row, 0).text
        for col in range(col_count):
            if table6.cell(row, col).text in listok:
                table6.cell(row, col).text = ""
            else:
                listok.append((table6.cell(row, col).text))

    for row in range(row_count):
        for col in range(col_count):
            if table6.cell(row, col).text == '':
                table6.cell(row - 1, col).merge(table6.cell(row, col))

    doc.save('новое_имя_файла.docx')
    word_file_path = 'новое_имя_файла.docx'
    response = FileResponse(open(word_file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="shablon_modeli_ugroz.docx"'
    return response


# todo вынести в отдельное  апи приложение
def read_capec(request):
    data = pd.read_excel('vygruzka_kapeka.xlsx')
    for index, row in data.iterrows():
        child_id = str(row['Related Attack Patterns'])
        for i in re.finditer(r'ChildOf:CAPEC ID:(\d+)', child_id):
            id_n = int(i.group(1))
            my_model = Capecs(id=row["'ID"], name=row['Name'], description=row['Description'],
                              typical_severity=row['Typical Severity'], execution_flow=row['Execution Flow'],
                              parent_id=id_n, consequences=row['Consequences'])
            my_model.save()
    return HttpResponse(content="capec recorded in db", status=200)


def read_bdus(request):
    data = pd.read_excel('bduxlsx.xlsx')
    for index, row in data.iterrows():
        my_model = Bdus(id=row["Идентификатор УБИ"], name=row['Наименование УБИ'], description=row['Описание'],
                        object_impact=row['Объект воздействия'],
                        violator=row['Источник угрозы (характеристика и потенциал нарушителя)'])
        my_model.save()
    return HttpResponse(content="bdu recorded in db", status=200)


def read_neg_pos(request):
    data = pd.read_excel('NP_list.xlsx')
    for index, row in data.iterrows():
        my_model = NegativeConsequences(
            id=row['Идентификатор'][2:],
            name=row['Наименование'],
            type=row['Ущерб']
        )
        my_model.save()
    return HttpResponse(content="NP recorded in db", status=200)


def test_bd(request):
    bdu = Bdus.objects.get(id=222)
    capecs = bdu.capecs.all()
    for c in capecs:
        print(c.name)
    print(bdu.capecs.all())
    return HttpResponse(content=bdu.capecs.all(), status=200)


def test(request):
    project = Projects.objects.get(name_project='хуй')
    table = generate_bdu_table(project)
    return HttpResponse(status=200, content=table.items())
