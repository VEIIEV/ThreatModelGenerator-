from django.urls import path
from .views import Projects_list, CreateProject, Show_Projects, Download_Project, read_capec, read_bdus, test_bd

app_name = 'projects'

urlpatterns = [
    path('projects/', Projects_list, name='projects'),
    path('create_project/', CreateProject.as_view(), name='CreateProject'),
    #todo создать view для  создания проекта и для отката на шаг назад
    # path('create_projects_up/', ..., name='CreateProjects_up'),
    # path('create_projects_down/', ..., name= 'CreateProjects_down'),
    path('downloadproject/', Download_Project, name='Download'),
    path('projects/<int:id>/', Show_Projects, name='detail_project'),
    path('capec/', read_capec, name='read_capec'),
    path('bdu/', read_bdus, name='read_bdus'),
    path('testdb/', test_bd, name='test_bd' ),
]
