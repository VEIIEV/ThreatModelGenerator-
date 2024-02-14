

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.views import View
from django.views.generic import ListView

from .models import User, Projcets
from . import views
from django.contrib.auth import views as auth_views, login, authenticate, logout


def Render_Main(request):
    return render(request, 'profils/main.html')


@login_required(login_url='profils:logun_users')
def Render_glavn(request):
    return render(request, 'profils/glavn_str.html')


class UserLoginView(View):

    def post(self, request):
        user = authenticate(username=request.POST['login'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('profils:rend_glavn')
        return render(request, 'profils/logun_users.html')

    def get(self, request):
        return render(request, 'profils/logun_users.html')


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('profils:main')


class Registration(View):
    def post(self, request):
        User.objects.create_user(username=request.POST['login'], password=request.POST['password'],
                                 email=request.POST['mail'])
        return render(request, 'profils/logun_users.html')

    def get(self, request):
        return render(request, 'profils/registration.html')


@login_required(login_url='profils:logun_users')
def MyAccount(request):
    return render(request, 'profils/my_account.html')






class CreateProject(View):

    def post(self, request):
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
        Projcets.objects.create(name_project=request.POST['name_project'],
                                is_wireless_tech=is_wireless,
                                is_cloud_tech=is_cloud,
                                is_virtual_tech=is_virtual,
                                protection_class=request.POST['protection_class'],
                                user_id=request.user.id)
        return render(request, 'profils/my_projects.html')

    def get(self, request):
        print(request)
        print(1)
        return render(request, 'profils/create_project.html')

@login_required(login_url='profils:logun_users')
def Projects(request):
    users_project = Projcets.objects.filter(user_id=request.user.id)
    data = {
        'projects': users_project
    }
    return render(request, 'profils/my_projects.html', context=data)

def Show_Projects(request,id):
    users_project = Projcets.objects.filter(id=id)
    return HttpResponse(f"Отображение статьи с id = {users_project[0].id}")

