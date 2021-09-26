from datetime import datetime
from os.path import basename
from typing import Iterable

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.functional import cached_property

from meta.models import ModelMeta

from users.models import User


class Committee(models.Model):
    """Internal committee.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Committee]'

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=120
    )

    description: 'models.TextField[str, str]' = models.TextField(
        'descripción'
    )

    manager: 'models.ForeignKey[User, User]' = models.ForeignKey(
        User, models.PROTECT, verbose_name='responsable'
    )

    class Meta:
        verbose_name = 'comisión'
        verbose_name_plural = 'comisiones'

        ordering = ('name',)


class DocumentMedia(models.Model):
    """Document and media files.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[DocumentMedia]'

    name: 'models.CharField[str, str]' = models.CharField('nombre', max_length=120)

    file: 'models.FileField' = models.FileField('archivo', upload_to='docs/')

    hidden: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'oculto', default=False,
        help_text='Ocultar el archivo en las listas'
    )

    category: 'models.CharField[str, str]' = models.CharField(
        'categoría', max_length=200, blank=True, default='',
        help_text=(
            'Los documentos con la misma categoría '
            'aparecerán agrupados juntos en la lista.'
        )
    )

    class Meta:
        verbose_name = 'documento'

    def __str__(self) -> str:
        return self.name

    def get_filename(self) -> str:
        return basename(self.file.name)


class Degree(models.Model):
    """Degree.
    """

    objects: 'models.Manager[Degree]'

    id: 'models.CharField[str, str]' = models.CharField('identificador', max_length=16, primary_key=True)

    name: 'models.CharField[str, str]' = models.CharField('nombre', max_length=120)

    is_master: 'models.BooleanField[bool, bool]' = models.BooleanField('es un máster', default=False)

    order: 'models.IntegerField[int, int]' = models.IntegerField(
        'orden', default=0,
        help_text='Las titulaciones con mayor orden salen antes'
    )

    class Meta:
        verbose_name = 'titulación'
        verbose_name_plural = 'titulaciones'

        ordering = ('-order', 'id')

    def __str__(self) -> str:
        return self.name


class Year(models.Model):
    """Academic Year.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Year]'

    year: 'models.IntegerField[int, int]' = models.IntegerField('año')

    degree: 'models.ForeignKey[Degree, Degree]' = models.ForeignKey(
        Degree, models.PROTECT, 'years',
        verbose_name='titulación'
    )

    telegram_group: 'models.CharField[str, str]' = models.CharField(
        'grupo de telegram', max_length=64,
        blank=True, null=True,
    )

    telegram_group_link: 'models.CharField[str, str]' = models.CharField(
        'enlace al grupo de telegram', max_length=64,
        blank=True, null=True,
    )

    class Meta:
        verbose_name = 'año'

        ordering = ('-degree__order', 'degree', 'year',)

    def __str__(self) -> str:
        return f'{self.degree.id} Año {self.year}'


class Group(models.Model):
    """Group of Students.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Group]'

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=64
    )

    number: 'models.IntegerField[int, int]' = models.IntegerField(
        'número de grupo', blank=True, null=True
    )

    year: 'models.ForeignKey[Year, Year]' = models.ForeignKey(
        Year, models.PROTECT, 'groups',
        verbose_name='año'
    )

    subgroups: 'models.IntegerField[int, int]' = models.IntegerField(
        'número de subgrupos', validators=[
            MinValueValidator(1), MaxValueValidator(4)
        ]
    )

    delegate: 'models.ForeignKey[User | None, User | None]' = models.ForeignKey(
        User, models.PROTECT, blank=True, null=True, related_name='delegate_group',
        verbose_name='delegado'
    )

    subdelegate: 'models.ForeignKey[User | None, User | None]' = models.ForeignKey(
        User, models.PROTECT, blank=True, null=True, related_name='subdelegate_group',
        verbose_name='subdelegado'
    )

    telegram_group: 'models.CharField[str, str]' = models.CharField(
        'grupo de telegram', max_length=64,
        blank=True, null=True,
    )

    telegram_group_link: 'models.CharField[str, str]' = models.CharField(
        'enlace al grupo de telegram', max_length=64,
        blank=True, null=True,
    )

    class Meta:
        verbose_name = 'grupo'

        ordering = ('-year__degree__order', 'year__degree', 'year', 'number')

        permissions = [
            ('can_link_group', 'Puede vincular un grupo de Telegram con un grupo de alumnos')
        ]

    def __str__(self) -> str:
        return f'{self.year} {self.name}'

    def subgroups_range(self) -> Iterable[int]:
        return range(1, self.subgroups + 1)

    def degree(self) -> Degree:
        return self.year.degree

    @property
    def display_title(self) -> str:
        return self.__str__()


class Meeting(ModelMeta, models.Model):
    """Assembly and commitees meetings.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Meeting]'

    date: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField('fecha')

    is_ordinary: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es una asamblea ordinaria', default=True
    )

    call: 'models.FileField' = models.FileField(
        'convocatoria', upload_to='meetings/'
    )

    minutes: 'models.FileField' = models.FileField(
        'acta', upload_to='meetings/', blank=True
    )

    minutes_approved: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'el acta se ha aprobado', default=False
    )

    documents: 'models.ManyToManyField[None, models.Manager[DocumentMedia]]' = models.ManyToManyField(
        DocumentMedia, verbose_name='documentos relacionados',
        blank=True
    )

    attendees: 'models.ManyToManyField[None, models.Manager[User]]' = models.ManyToManyField(
        User, 'meetings_attended',
        verbose_name='asistentes', blank=True
    )

    absents: 'models.ManyToManyField[None, models.Manager[User]]' = models.ManyToManyField(
        User, 'meetings_absent',
        verbose_name='ausencias justificadas', blank=True
    )

    _metadata = {
        'title': '__str__',
    }

    class Meta:
        verbose_name = 'asamblea de alumnos'
        verbose_name_plural = 'asambleas de alumnos'

        ordering = ('-date',)

    def __str__(self) -> str:
        when = date(self.date, 'j F Y')
        return f'Asamblea de Alumnos {when}'

    def get_absolute_url(self) -> str:
        return reverse('heart:meetings_update', args=[self.pk])


class PeopleGroup(models.Model):
    """Groups of relevant people.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[PeopleGroup]'

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=120, unique=True
    )

    members: 'models.ManyToManyField[None, models.Manager[User]]' = models.ManyToManyField(
        User, through='PeopleGroupMember'
    )

    order: 'models.IntegerField[int, int]' = models.IntegerField(
        'orden', default=1,
        help_text='Se ordena de forma creciente (menor número sale antes).'
    )

    is_hidden: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'ocultar grupo', default=False,
        help_text=(
            'Ocultar los miembros de este colectivo '
            'en las vistas públicas del sitio web'
        )
    )

    show_in_meetings: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'mostrar en asambleas', default=True,
        help_text=(
            'Mostrar los miembros de este colectivo '
            'en las listas de asistencia de las asambleas'
        )
    )

    class Meta:
        verbose_name = 'grupo de gente importante'
        verbose_name_plural = 'grupos de gente importante'

        ordering = ('order', 'name')

    def __str__(self) -> str:
        return self.name


class PeopleGroupMember(models.Model):
    """Members of groups of relevant people.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[PeopleGroupMember]'

    group: 'models.ForeignKey[PeopleGroup, PeopleGroup]' = models.ForeignKey(
        PeopleGroup, models.CASCADE, verbose_name='grupo'
    )

    user: 'models.ForeignKey[User, User]' = models.ForeignKey(
        User, models.CASCADE, verbose_name='usuario'
    )

    title: 'models.CharField[str, str]' = models.CharField(
        'título', max_length=120, default='', blank=True
    )

    order: 'models.IntegerField[int, int]' = models.IntegerField(
        'orden', default=1,
        help_text='Se ordena de forma creciente (menor número sale antes).'
    )

    class Meta:
        verbose_name = 'grupo de gente importante'
        verbose_name_plural = 'grupos de gente importante'

        ordering = ('order', 'user__first_name')

    def __str__(self) -> str:
        txt = f'{self.user.email} en {self.group}'

        if self.title:
            txt += f' ({self.title})'

        return txt

    @cached_property
    def name(self) -> str:
        return self.user.get_full_name()
