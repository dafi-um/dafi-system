from os.path import basename

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse

from meta.models import ModelMeta

User = get_user_model()


class Group(models.Model):
    '''Group of Students'''

    GII = 'GII'
    MNTI = 'MNTI'
    MBD = 'MBD'

    COURSES = (
        (GII, 'Grado en Ingeniería Informática'),
        (MNTI, 'Máster en Nuevas Tecnologías de la Informática'),
        (MBD, 'Máster en Big Data'),
    )

    name = models.CharField(
        'nombre', max_length=64
    )

    number = models.IntegerField(
        'número de grupo', blank=True, null=True
    )

    year = models.IntegerField(
        'año'
    )

    course = models.CharField(
        'estudios', max_length=6, choices=COURSES, default=GII
    )

    subgroups = models.IntegerField(
        'número de subgrupos', validators=[
            MinValueValidator(1), MaxValueValidator(4)
        ]
    )

    delegate = models.ForeignKey(
        User, models.PROTECT, blank=True, null=True, related_name='delegate_group',
        verbose_name='delegado'
    )

    subdelegate = models.ForeignKey(
        User, models.PROTECT, blank=True, null=True, related_name='subdelegate_group',
        verbose_name='subdelegado'
    )

    telegram_group = models.CharField(
        'grupo de telegram', max_length=64, blank=True, default=''
    )

    telegram_group_link = models.CharField(
        'enlace al grupo de telegram', max_length=64, blank=True, default=''
    )

    class Meta():
        verbose_name = 'grupo'

        ordering = ('course', 'year', 'number')

        permissions = [
            ('can_link_group', 'Puede vincular un grupo de Telegram con un grupo de alumnos')
        ]

    def __str__(self):
        return 'Año {} {}'.format(self.year, self.name)

    def subgroups_range(self):
        return range(1, self.subgroups + 1)


class Meeting(ModelMeta, models.Model):
    '''Assembly and commitees meetings'''

    date = models.DateTimeField('fecha')

    call = models.FileField(
        'convocatoria', upload_to='meetings/'
    )

    minutes = models.FileField(
        'acta', upload_to='meetings/', blank=True
    )

    attendees = models.ManyToManyField(
        User, 'meetings_attended',
        verbose_name='asistentes', blank=True
    )

    absents = models.ManyToManyField(
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

    def __str__(self):
        return 'Asamblea de Alumnos {}'.format(date(self.date, 'j F Y'))

    def get_absolute_url(self):
        return reverse('heart:meetings_update', args=[self.pk])


class PeopleGroup(models.Model):
    '''Groups of relevant people'''

    name = models.CharField(
        'nombre', max_length=120, unique=True
    )

    members = models.ManyToManyField(
        User, through='PeopleGroupMember'
    )

    is_hidden = models.BooleanField(
        'ocultar grupo', default=False,
        help_text=(
            'Ocultar los miembros de este colectivo '
            'en las vistas públicas del sitio web'
        )
    )

    show_in_meetings = models.BooleanField(
        'mostrar en asambleas', default=True,
        help_text=(
            'Mostrar los miembros de este colectivo '
            'en las listas de asistencia de las asambleas'
        )
    )

    class Meta:
        verbose_name = 'grupo de gente importante'
        verbose_name_plural = 'grupos de gente importante'

    def __str__(self):
        return self.name


class PeopleGroupMember(models.Model):
    '''Members of groups of relevant people'''

    group = models.ForeignKey(
        PeopleGroup, models.CASCADE, verbose_name='grupo'
    )

    user = models.ForeignKey(
        User, models.CASCADE, verbose_name='usuario'
    )

    title = models.CharField(
        'título', max_length=120, default='', blank=True
    )

    class Meta:
        verbose_name = 'grupo de gente importante'
        verbose_name_plural = 'grupos de gente importante'

    def __str__(self):
        txt = '{} en {}'.format(self.user.email, self.group)

        if self.title:
            txt += ' ({})'.format(self.title)

        return txt


class DocumentMedia(models.Model):
    '''Document and media files'''

    name = models.CharField('nombre', max_length=120)

    file = models.FileField('archivo', upload_to='docs/')

    hidden = models.BooleanField(
        'oculto', default=False,
        help_text='Ocultar el archivo en las listas'
    )

    category = models.CharField(
        'categoría', max_length=200, blank=True, default='',
        help_text=(
            'Los documentos con la misma categoría '
            'aparecerán agrupados juntos en la lista.'
        )
    )

    class Meta:
        verbose_name = 'documento'

    def __str__(self):
        return self.name

    def get_filename(self):
        return basename(self.file.name)
