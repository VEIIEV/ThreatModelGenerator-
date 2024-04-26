import re
from datetime import date
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
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
from .models import Projects, Capecs, Bdus, RPersons, NegativeConsequences, ObjectOfInfluences, Violators, ViolatorLvls, \
    Components
from .tasks import celery_generate_doc
from .utils import genereate_neg_con_table, generate_obj_inf_table, generate_violators_type_table, \
    generate_violators_potential_table, form_bdus_list_for, generate_bdu_table, generate_doc


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
                                       'objs': ObjectOfInfluences.objects.all().order_by('id'),
                                       'ob_ids': ob_ids,
                                       'add_options': add_options})
            case '6':
                object_to_response = {}
                for obj in project.object_inf.all():
                    object_to_response[obj.name] = obj.components.all()
                component_ids = project.object_inf.values_list('id', flat=True)
                return render(request, '../templates/projects/create_project_6.html',
                              context={'project': project,
                                       'objects': object_to_response,
                                       'component_ids': component_ids})

            case '7':

                v_lvl_names = project.get_violator_lvl_names()
                return render(request, '../templates/projects/create_project_7.html',
                              context={'project': project,
                                       'violators': ViolatorLvls.objects.all(),
                                       'v_lvl_names': v_lvl_names})
            case '8':

                # todo добавить кнопку для выгрузки каждой таблице отдельно как excel
                # todo добавить кнопку для выгрузки всего ворд документа
                return render(request, '../templates/projects/create_project_8.html', context={'project': project})

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
                names = []
                appointments = []
                for key, value in request.POST.items():
                    if re.search("rperson_name", key) is not None:
                        names.append(value)
                    if re.search("appointment", key) is not None:
                        appointments.append(value)
                for n, a in zip(names, appointments):
                    r_person = RPersons.objects.create(name=n, appointment=a, projects=project)
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
                ids = data.getlist('options')
                for np_id in ids:
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
                                       'objs': ObjectOfInfluences.objects.all().order_by('id'),
                                       'add_options': add_options})
                pass
            case '5':
                # TODO должно быть выбрано хотя бы 1 обязательное поле
                data = QueryDict(request.body)
                ids = data.getlist('options')
                print(data)

                # мне нужно параллельно составить словарь где ключ объект, значение список компонентов
                object_to_response = {}
                for obj_id in ids:
                    obj = ObjectOfInfluences.objects.get(id=int(obj_id))
                    project.object_inf.add(obj)
                    # составление списка компонентов для респонса
                    object_to_response[obj.name] = obj.components.all()

                project.is_grid = True if ("A_grid system" in data) else False
                project.is_virtual = True if ("A_virtual system" in data) else False
                project.is_wireless = True if ("A_wireless system" in data) else False
                project.is_cloud = True if ("A_cloud system" in data) else False
                project.stage = 6
                project.save()

                return render(request, '../templates/projects/create_project_6.html',
                              context={'project': project,
                                       'objects': object_to_response, })

            case '6':
                data = QueryDict(request.body)
                print(data)
                for key in data.keys():
                    if re.search("D_", key) is not None:
                        component_id = data.get(key)
                        component = Components.objects.get(id=int(component_id))
                        project.components.add(component)
                project.stage = 7
                project.save()
                return render(request, '../templates/projects/create_project_7.html',
                              context={'project': project,
                                       'violators': ViolatorLvls.objects.all()})

            case '7':
                data = QueryDict(request.body)
                ids = data.getlist('options')
                print(data)
                for vio_lvl in ids:
                    project.violator_lvls.add(ViolatorLvls.objects.get(lvl=vio_lvl))
                    violators = ViolatorLvls.objects.get(lvl=vio_lvl).violators.all()
                    for violator in violators:
                        project.violators.add(violator)
                project.stage = 8
                project.save()

                return render(request, '../templates/projects/create_project_8.html', context={'project': project})
            case '8':
                # todo дело сделано, показываем итог и выгружаем док
                response = generate_doc(project)
                return response


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
        if project_id is None:
            return HttpResponseBadRequest("Missing 'id' parameter")

        stage = request.GET.get('stage')
        if stage is None:
            return HttpResponseBadRequest("Missing 'stage' parameter")

        project = Projects.objects.get(id=project_id)
        if (int(stage) < project.stage):
            project.roll_back_to_stage(stage)
        match project.type:
            case 'KII':
                signif_lvl = max(int(request.POST['confidentiality']), )

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
def delete_project(request: HttpRequest):
    project_id = request.GET.get('id')
    project = Projects.objects.get(id=project_id)
    project.delete()
    return redirect('projects:projects')


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


def download_project(request: HttpRequest):
    project = Projects.objects.get(id=request.GET.get('id'))

    word_file_path = project.doc
    response = FileResponse(open(word_file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="новое_имя_файла.docx"'
    return response


def generate_project(request: HttpRequest):
    project = Projects.objects.get(id=request.GET.get('id'))
    project.doc = 'loading'
    project.save()
    celery_generate_doc.delay(project.id)
    return render(request, '../templates/projects/create_project_8.html', context={'project': project})


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
    return render(request, '../templates/projects/test.html')
