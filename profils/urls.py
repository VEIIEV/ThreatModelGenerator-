from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.urls import path, reverse_lazy
from .views import Render_Main, UserLoginView, UserLogoutView, Render_glavn, Registration, MyAccount, Projects, \
    CreateProject, Show_Projects

app_name = 'profils'

urlpatterns = [
    path('main/', Render_Main, name='main'),
    path('logun_users/', UserLoginView.as_view(), name='logun_users'),
    path('logout_users/', UserLogoutView.as_view(), name='logout_users'),
    path('glavn_str/', Render_glavn, name='rend_glavn'),

    path('password-reset/',
         PasswordResetView.as_view(
             template_name="profils/password_reset_form.html",
             email_template_name="profils/password_reset_email.html",
             success_url=reverse_lazy("profils:password_reset_done")
         ),
         name='password_reset'),

    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name="profils/password_reset_done.html"),
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name="profils/password_reset_confirm.html",
                                          success_url=reverse_lazy("profils:password_reset_complete")),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         PasswordResetDoneView.as_view(template_name="profils/password_reset_complete.html"),
         name='password_reset_complete'),

    path('registration/', Registration.as_view(), name='Registration'),
    path('projects/<int:id>/', Show_Projects, name='detail_project'),
    path('my_account/', MyAccount, name='MyAccount'),
    path('projects/', Projects, name='projects'),
    path('create_projects/', CreateProject.as_view(), name='CreateProjects'),

]
