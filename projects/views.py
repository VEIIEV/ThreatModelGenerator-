import re

import pandas as pd
import xlwt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest, QueryDict
from django.shortcuts import render
from django.views import View

from profils.models import User
from .models import Projects, Capecs, Bdus, RPersons, NegativeConsequences, ObjectOfInfluences, Violators, ViolatorLvls
from .utils import create_word, genereate_neg_con_table, generate_obj_inf_table


# todo накатить фронт,


class CreateProject(View):

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
                return render(request, '../templates/projects/create_project_2.html', context={'project': project})
            case '3':
                return render(request, '../templates/projects/create_project_3.html', context={'project': project})
            case '4':
                return render(request, '../templates/projects/create_project_4.html',
                              context={'project': project,
                                       'negative_consequences': NegativeConsequences.objects.all()})
            case '5':
                return render(request, '../templates/projects/create_project_5.html',
                              context={'project': project,
                                       'objs': ObjectOfInfluences.objects.all()})
            case '6':
                return render(request, '../templates/projects/create_project_6.html', context={'project': project,
                                                                                               'violators': ViolatorLvls.objects.all()})
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
            # todo написать функцию для модели project, который откатывает изменения для соот стадии
            ...

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
                return render(request, '../templates/projects/create_project_3.html', context={'project': project})
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
                return render(request, '../templates/projects/create_project_5.html', context={'project': project,
                                                                                               'objs': ObjectOfInfluences.objects.all()})
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

                return render(request, '../templates/projects/create_project_6.html', context={'project': project,
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


def Download_Project(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users Data')  # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Username', 'First Name', 'Last Name', 'Email Address', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
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
    table = generate_obj_inf_table(project)
    return HttpResponse(status=200, content=table)
