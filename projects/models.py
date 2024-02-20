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

class Risks(models.Model):
    Identifier = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    the_object_of_influence = models.CharField(max_length=300)
    components = models.CharField(max_length=300)
    implementation_methods = models.CharField(max_length=400)
    potential_violator = models.CharField(max_length=400)
    protection_measures = models.CharField(max_length=400)