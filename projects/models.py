from audioop import reverse

from django.db import models

from profils.models import User


class Projects(models.Model):
    """Модель проектов"""
    name_project = models.CharField(max_length=255, default='Тестовый', unique=False, null=False, blank=False)
    is_wireless_tech = models.BooleanField(default=True)
    is_cloud_tech = models.BooleanField(default=True)
    is_virtual_tech = models.BooleanField(default=True)
    protection_class = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.protection_class} {self.is_virtual_tech}"

    def get_absolute_url(self):
        return reverse('profils:detail_project', kwargs={'id': self.pk})


class R_person(models.Model):
    """Ответственные за проект"""
    name = models.CharField(max_length=255)
    appointment = models.CharField(max_length=255)

class Capec(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    typical_severity = models.CharField(max_length=20)
    execution_flow = models.CharField(max_length=255)
    parent_id = models.IntegerField(null=True, blank=True, default=None)
    child_id = models.IntegerField(null=True, blank=True, default=None)
    consequences = models.CharField(max_length=255)
class Bdu(models.Model):
    """Название, условное обозначение (вида УБИ.001), описание,
объект воздействия, последствия реализации угрозы, форейн ки
на капек, (форейн ки на нарушителей)/(хранить нарушителей как
список), флаги:
object_impact- распарсить и спарсить
"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    object_impact = models.CharField(max_length=500)
    violator = models.CharField(max_length=255)
    capecs = models.ManyToManyField(Capec)
