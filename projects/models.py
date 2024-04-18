from django.urls import reverse

from django.db import models
from django.utils.translation import gettext_lazy as _

from profils.models import User


class ViolatorLvls(models.Model):
    lvl = models.IntegerField(primary_key=True)
    alias = models.CharField(max_length=2550, blank=True, null=True)
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
    capecs = models.ManyToManyField(Capecs, related_name='capecs')  # кирилл ты ебло

    is_grid = models.BooleanField(null=True)
    is_virtual = models.BooleanField(null=True)
    is_wireless = models.BooleanField(null=True)
    is_cloud = models.BooleanField(null=True)


class ObjectOfInfluences(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True, null=True)
    bdus = models.ManyToManyField(Bdus, related_name='bdus')  # кирилл ты ебло


class Components(models.Model):
    '''
    В бд заполнены связи для 1 2 6 объекта
    '''
    name = models.CharField(max_length=2550)
    alias = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=3000, blank=True)
    object_of_influences = models.ManyToManyField(ObjectOfInfluences, related_name='components')  # вот тут молодец


class SPMethods(models.Model):
    '''
      В бд заполнены связи для компонентов  биос  и ОС
      '''
    name = models.CharField(max_length=2550)
    alias = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(max_length=3000, blank=True)
    components = models.ManyToManyField(Components, related_name='spmethods')  # вот тут молодец
    violator_lvls = models.CharField(max_length=255, blank=True, null=True)


class Tactics(models.Model):
    '''
         В бд заполнены связи для СП 1.1 1.2  2.1
    '''
    name = models.CharField(max_length=2550)
    alias = models.CharField(max_length=255, blank=True, null=True)
    technique = models.TextField(max_length=3000, blank=True)
    spmethods = models.ManyToManyField(SPMethods, related_name='tactics')  # вот тут молодец


class NegativeConsequences(models.Model):
    name = models.CharField(max_length=25500)
    type = models.CharField(max_length=25500)

    object_of_influence = models.ManyToManyField(ObjectOfInfluences, through='KindOfOfInfluences')


class KindOfOfInfluences(models.Model):
    object_of_inf = models.ForeignKey(ObjectOfInfluences, on_delete=models.CASCADE)
    neg_cons = models.ForeignKey(NegativeConsequences, on_delete=models.CASCADE)
    kind_of_inf = models.CharField(max_length=25500, null=True, blank=True)


class NormativeDocuments(models.Model):
    class Meta:
        unique_together = ["type", "name"]

    class SystemTypes(models.TextChoices):
        GYS = "GYS", _("State Information System")
        ISPDN = "ISP", _("Personal Data Information System")
        KII = "KII", _("Critical Information Infrastructure")

    type = models.CharField(
        max_length=3,
        choices=SystemTypes.choices,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=1000, blank=True, null=True)


class Projects(models.Model):
    """Модель проектов"""

    # TODO возможно необходимо добавить связь многие ко многим с бду
    class SystemTypes(models.TextChoices):
        GYS = "GYS", _("Государственная информационная система")
        ISPDN = "ISP", _("Информационная система персональных данных")
        KII = "KII", _("Объект критической информационной инфраструктуры")

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

    components = models.ManyToManyField(Components, related_name='projects')

    is_grid = models.BooleanField(null=True)
    is_virtual = models.BooleanField(null=True)
    is_wireless = models.BooleanField(null=True)
    is_cloud = models.BooleanField(null=True)

    violators = models.ManyToManyField(Violators)
    violator_lvls = models.ManyToManyField(ViolatorLvls, related_name='projects')

    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # def __str__(self):
    #     return f"{self.protection_class} {self.is_virtual_tech}"

    def get_absolute_url(self):
        return reverse('projects:detail_project', kwargs={'id': self.pk})

    def get_violator_lvl_names(self):
        violators = set()
        for violator in self.violators.all():
            violators.add(violator.lvl.name)
        return violators

    def roll_back_to_stage(self, stage: int) -> None:
        match int(stage):
            case 1:
                self.violators.clear()
                self.object_inf.clear()
                self.components.clear()
                self.negative_consequences.clear()
                RPersons.objects.filter(projects=self).delete()
                self.system_lvl = None
                self.type = None
                self.stage = 1
                self.save()
            case 2:
                self.violators.clear()
                self.object_inf.clear()
                self.components.clear()
                self.negative_consequences.clear()
                self.system_lvl = None
                self.stage = 2
                self.save()
            case 3:
                self.violators.clear()
                self.object_inf.clear()
                self.components.clear()
                self.negative_consequences.clear()
                self.stage = 3
                self.save()
            case 4:
                self.violators.clear()
                self.object_inf.clear()
                self.components.clear()
                self.negative_consequences.clear()
                self.stage = 4
                self.save()
            case 5:
                self.violators.clear()
                self.object_inf.clear()
                self.components.clear()
                self.stage = 5
                self.save()
            case 6:
                self.violators.clear()
                self.components.clear()
                self.stage = 6
                self.save()
            case 7:
                self.violators.clear()
                self.stage = 7
                self.save()


class RPersons(models.Model):
    """Ответственные за проект"""
    name = models.CharField(max_length=255)
    appointment = models.CharField(max_length=255)
    projects = models.ForeignKey(Projects, on_delete=models.PROTECT, null=True, related_name='r_persons')
