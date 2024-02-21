from django.contrib import admin

from projects.models import Capec,Bdu


class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Capec, AuthorAdmin)
admin.site.register(Bdu, AuthorAdmin)