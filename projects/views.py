import pandas as pd
import xlwt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.views import View
import re

from profils.models import User
from .models import Projects, Capecs, Bdus, RPersons


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
                return render(request, '../templates/projects/create_project_4.html', context={'project': project})
            case '5':
                pass
            case '6':
                pass
            case '7':
                pass

    def post(self, request: HttpRequest):
        stage = request.GET.get('stage')
        project_id = int(request.GET.get('id'))
        project = Projects.objects.get(id=project_id)

        if (int(stage) < project.stage):
            # todo написать менеджер для модели project, который откатывает изменения для соот стадии
            ...

        match stage:
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
                return render(request, '../templates/projects/create_project_4.html', context={'project': project})
            case '4':
                pass
            case '5':
                pass
            case '6':
                pass
            case '7':
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


# Читаем данные из Excel файла

# data = pd.read_excel('vygruzka_kapeka.xlsx')
# # Проходим по каждой строке данных и сохраняем их в БД Django
# for index, row in data.iterrows():
#     child_id = row['Related Attack Patterns']
#     for i in re.finditer(r'ChildOf:CAPEC ID:(\d+)', child_id):
#         id = int(i.group(1))
#         my_model = Capec(id=row['ID'], name=row['Name'], description=row['Description'],
#                          typical_severity=row['Typical Severity'], execution_flow=row['Execution Flow'],
#                          child_id=id,consequences=row['Consequences'])
#         my_model.save()

# id = models.IntegerField(primary_key=True)
# name = models.CharField(max_length=255)
# description = models.CharField(max_length=255)
# typical_severity = models.CharField(max_length=20)
# execution_flow = models.CharField(max_length=255)
# parent_id = models.IntegerField(null=True, blank=True, default=None)
# child_id = models.IntegerField(null=True, blank=True, default=None)
# consequences = models.CharField(max_length=255)


# todo вынести в апи
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
