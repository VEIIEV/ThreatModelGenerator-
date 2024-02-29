import pandas as pd
import xlwt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, request
from django.shortcuts import render
from django.views import View

from profils.models import User
from .models import Projects, Bdus


class CreateProject(View):
    # id = models.IntegerField(primary_key=True)
    # name = models.CharField(max_length=255)
    # description = models.CharField(max_length=255)
    # object_impact = models.CharField(max_length=500)
    # violator = models.CharField(max_length=255)
    # capecs = models.ManyToManyField(Capec)
    def post(self, request):
        #data = pd.read_excel('bduxlsx.xlsx')
        #for index, row in data.iterrows():
        #    my_model = Bdu(id=row["Идентификатор УБИ"], name=row['Наименование УБИ'], description=row['Описание'],
        #                               object_impact=row['Объект воздействия'], violator=row['Источник угрозы (характеристика и потенциал нарушителя)'])
        #    my_model.save()

        if request.POST['is_wireless_tech'] == 'True':
            is_wireless = True
        else:
            is_wireless = False
        if request.POST['is_cloud_tech'] == 'True':
            is_cloud = True
        else:
            is_cloud = False
        if request.POST['is_virtual_tech'] == 'True':
            is_virtual = True
        else:
            is_virtual = False

        print('1')
        Projects.objects.create(name_project=request.POST['name_project'],
                                is_wireless_tech=is_wireless,
                                is_cloud_tech=is_cloud,
                                is_virtual_tech=is_virtual,
                                protection_class=request.POST['protection_class'],
                                user_id=request.user.id)
        return render(request, '../templates/projects/my_projects.html')


    def get(self, request):
        return render(request, '../templates/projects/create_project.html')


@login_required(login_url='profils:logun_users')
def Projects_list(request):
    paginate_by = 4
    users_project = Projects.objects.filter(user_id=request.user.id)
    paginator = Paginator(users_project, 2)
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
