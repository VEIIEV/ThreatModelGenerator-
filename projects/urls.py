from django.urls import path

from .views import Projects_list, CreateProject, Show_Projects, read_capec, read_bdus, test_bd, \
    read_neg_pos, test, ChooseSystemLvl, delete_project, generate_project, \
    download_project

app_name = 'projects'

urlpatterns = [
    path('projects/', Projects_list, name='projects'),
    path('create_project/', CreateProject.as_view(), name='CreateProject'),
    path('delete_project/', delete_project, name='delete_project'),
    path('choose_system_lvl/', ChooseSystemLvl.as_view(), name='ChooseSystemLvl'),
    path('generate_project/', generate_project, name='generate_project'),
    path('downloadproject/', download_project, name='download_project'),
    path('projects/<int:id>/', Show_Projects, name='detail_project'),
    path('capec/', read_capec, name='read_capec'),
    path('bdu/', read_bdus, name='read_bdus'),
    path('testdb/', test_bd, name='test_bd'),
    path('np/', read_neg_pos, name='read_neg_pos'),
    path('test/', test, name='test')
]
