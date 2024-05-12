from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from projects.models import NegativeConsequences
from .models import User


def Render_Main(request):
    return render(request, '../templates/profils/main.html')


@login_required(login_url='profils:logun_users')
def Render_glavn(request):
    return render(request, '../templates/profils/glavn_str.html')


class UserLoginView(View):

    def post(self, request):
        a = HttpResponse()
        user = authenticate(username=request.POST['login'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('profils:rend_glavn')
        return render(request, '../templates/profils/logun_users.html')

    def get(self, request):
        return render(request, '../templates/profils/logun_users.html')


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('profils:main')


class Registration(View):
    def post(self, request):
        User.objects.create_user(username=request.POST['login'], password=request.POST['password'],
                                 email=request.POST['mail'])
        return render(request, '../templates/profils/logun_users.html')

    def get(self, request):
        return render(request, '../templates/profils/registration.html')


# @login_required(login_url='profils:logun_users')
# def MyAccount(request):
#     return render(request, 'profils/my_account.html')

class MyAccount(View):
    def post(self, request):
        if request.user.is_authenticated:
            if request.POST['newpassword'] == '':
                if request.user.is_authenticated:
                    profile = User.objects.get(id=request.user.id)
                    profile.first_name = request.POST['firstname']
                    profile.last_name = request.POST['lastname']
                    profile.email = request.POST['email']
                    profile.save()
                    return render(request, '../templates/profils/my_account.html')
                else:
                    return render(request, '../templates/profils/logun_users.html')
            else:
                u = User.objects.get(id=request.user.id)
                u.set_password(request.POST['newpassword'])
                u.save()
                return render(request, '../templates/profils/my_account.html')
        else:
            return render(request, '../templates/profils/logun_users.html')
    def get(self, request):
        if request.user.is_authenticated:
            profile = User.objects.get(id=request.user.id)

            data = {
                'user': profile
            }
            return render(request, '../templates/profils/my_account.html', context=data)
        else:
            return render(request, '../templates/profils/logun_users.html')


class creating_custom_NE(View):

    def post(self,request:HttpRequest):
        NegativeConsequences.objects.create(name=request.POST['name_negative'], type=request.POST['type_negative'])
        return render(request, '../templates/profils/creating_custom_NE.html')

    # class NegativeConsequences(models.Model):
    #     name = models.CharField(max_length=255)
    #     type = models.CharField(max_length=255)
    #     objectofinfluence = models.ManyToManyField(ObjectOfInfluence)
    def get(self, request):
        return render(request, '../templates/profils/creating_custom_NE.html')