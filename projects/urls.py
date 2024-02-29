from django.urls import path
from .views import Projects_list, CreateProject, Show_Projects, Download_Project, read_capec, read_bdus

app_name = 'projects'

urlpatterns = [
    path('projects/', Projects_list, name='projects'),
    path('create_projects/', CreateProject.as_view(), name='CreateProjects'),
    path('downloadproject/', Download_Project, name='Download'),
    path('projects/<int:id>/', Show_Projects, name='detail_project'),
    path('capec/', read_capec, name='read_capec'),
    path('bdu/', read_bdus, name='read_bdus')
]
