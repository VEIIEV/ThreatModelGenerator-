from django.contrib import admin

from projects.models import Capecs, Bdus


# id = models.IntegerField(primary_key=True)
#     name = models.CharField(max_length=255)
#     description = models.CharField(max_length=2000)
#     object_impact = models.CharField(max_length=500)
#     violator = models.CharField(max_length=255)
#     capecs = models.ManyToManyField(Capec, blank=True)
@admin.register(Capecs)
class CapecAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'typical_severity', 'parent_id', 'child_id', 'consequences')
    list_filter_links = ('name', 'description')
    list_editable = ( 'name', 'description', 'typical_severity', 'parent_id', 'child_id', 'consequences')

@admin.register(Bdus)
class BduAdmin(admin.ModelAdmin):
    filter_horizontal = ('capecs',)
