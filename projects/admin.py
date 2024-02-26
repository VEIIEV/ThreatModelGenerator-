from django.contrib import admin

from projects.models import Capecs,Bdus


class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Capecs, AuthorAdmin)
admin.site.register(Bdus, AuthorAdmin)