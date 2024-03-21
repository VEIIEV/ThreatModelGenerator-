from django.urls import reverse

from django.db import models
from django.utils.translation import gettext_lazy as _

from profils.models import User


class ViolatorLvls(models.Model):
    lvl = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=2550, blank=True, null=True)
    description = models.TextField(max_length=3000)


class Violators(models.Model):
    """Нарушителей – тип нарушителя, уровень возможности (В1 – В4),
    type - вид (внутренний, внешний, оба) = (1, 2, 3)
    potential - потенциал (низкий, средний, высокий) = (1,2,3) ( )
    Возможные цели (мотивация) реализации угроз безопасности информации,
    (см методику от 05.02.2021 приложение 8,9)"""
    name = models.CharField(max_length=255)
    lvl = models.ForeignKey(ViolatorLvls, on_delete=models.PROTECT, related_name='violators')
    type = models.IntegerField()
    potential = models.IntegerField()
    motives = models.CharField(max_length=3000, blank=True, null=True)
    # TODO определиться нужна ли свзяь нарушителей с бду, пока не уверен
    # TODO заполнить поле мотивов



class Capecs(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20000)
    description = models.CharField(max_length=20000)
    typical_severity = models.CharField(max_length=20000)
    execution_flow = models.CharField(max_length=20000)
    parent_id = models.IntegerField(null=True, blank=True, default=None)
    child_id = models.IntegerField(null=True, blank=True, default=None)
    consequences = models.CharField(max_length=20000)


class Bdus(models.Model):
    """Название, условное обозначение (вида УБИ.001), описание,
объект воздействия, последствия реализации угрозы, форейн ки
на капек, (форейн ки на нарушителей)/(хранить нарушителей как
список), флаги:
object_impact- распарсить и спарсить
"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=2000)
    description = models.CharField(max_length=20000)
    object_impact = models.CharField(max_length=500)
    violator = models.CharField(max_length=255)
    capecs = models.ManyToManyField(Capecs,related_name='capecs')

    is_grid = models.BooleanField(null=True)
    is_virtual = models.BooleanField(null=True)
    is_wireless = models.BooleanField(null=True)
    is_cloud = models.BooleanField(null=True)

class ObjectOfInfluences(models.Model):
    name = models.CharField(max_length=255)
    bdu = models.ManyToManyField(Bdus)


class NegativeConsequences(models.Model):
    name = models.CharField(max_length=25500)
    type = models.CharField(max_length=25500)
    objectofinfluence = models.ManyToManyField(ObjectOfInfluences)


class Projects(models.Model):
    """Модель проектов"""
    #TODO возможно необходимо добавить связь многие ко многим с бду
    class SystemTypes(models.TextChoices):
        GYS = "GYS", _("State Information System")
        ISPDN = "ISP", _("Personal Data Information System")
        KII = "KII", _("Critical Information Infrastructure")

    name_project = models.CharField(max_length=255, default='new project', unique=False, null=False, blank=False)
    description = models.TextField(max_length=10000, null=True, blank=True)
    stage = models.IntegerField(default=1)
    type = models.CharField(
        max_length=3,
        choices=SystemTypes.choices,
        blank=True,
        null=True
    )
    system_lvl = models.IntegerField(null=True, blank=True)

    negative_consequences = models.ManyToManyField(NegativeConsequences)

    object_inf = models.ManyToManyField(ObjectOfInfluences)

    is_grid = models.BooleanField(null=True)
    is_virtual = models.BooleanField(null=True)
    is_wireless = models.BooleanField(null=True)
    is_cloud = models.BooleanField(null=True)

    violators = models.ManyToManyField(Violators)

    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # def __str__(self):
    #     return f"{self.protection_class} {self.is_virtual_tech}"

    def get_absolute_url(self):
        return reverse('projects:detail_project', kwargs={'id': self.pk})

    def roll_back_to_stage(self, stage: int) -> None:
        match stage:
            case 1:
                self.violators.through.objects.all().delete()
                self.object_inf.through.objects.all().delete()
                self.negative_consequences.through.objects.all().delete()
                self.system_lvl= None
                self.type = None
                self.stage=1
                self.save()
            case 2:
                self.violators.through.objects.all().delete()
                self.object_inf.through.objects.all().delete()
                self.negative_consequences.through.objects.all().delete()
                self.type = None
                self.stage = 2
                self.save()
            case 3:
                self.violators.through.objects.all().delete()
                self.object_inf.through.objects.all().delete()
                self.negative_consequences.through.objects.all().delete()
                self.stage = 3
                self.save()
            case 4:
                pass
            case 5:
                pass
            case 6:
                pass

class RPersons(models.Model):
    """Ответственные за проект"""
    name = models.CharField(max_length=255)
    appointment = models.CharField(max_length=255)
    projects = models.ForeignKey(Projects, on_delete=models.PROTECT, null=True, related_name='r_persons')


