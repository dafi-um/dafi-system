from os.path import basename

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.functional import cached_property

from meta.models import ModelMeta

User = get_user_model()


class Committee(models.Model):
    '''Internal committee'''

    name = models.CharField(
        'nombre', max_length=120
    )

    description = models.TextField(
        'descripción'
    )

    manager = models.ForeignKey(
        User, models.PROTECT, verbose_name='responsable'
    )

    class Meta:
        verbose_name = 'comisión'
        verbose_name_plural = 'comisiones'

        ordering = ('name',)


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


class Degree(models.Model):
    '''Degree'''

    id = models.CharField('identificador', max_length=16, primary_key=True)

    name = models.CharField('nombre', max_length=120)

    is_master = models.BooleanField('es un máster', default=False)

    order = models.IntegerField(
        'orden', default=0,
        help_text='Las titulaciones con mayor orden salen antes'
    )

    class Meta:
        verbose_name = 'titulación'
        verbose_name_plural = 'titulaciones'

        ordering = ('-order', 'id')

    def __str__(self):
        return self.name


class Year(models.Model):
    '''Academic Year'''

    year = models.IntegerField('año')

    degree = models.ForeignKey(
        Degree, models.PROTECT, 'years',
        verbose_name='titulación'
    )

    telegram_group = models.CharField(
        'grupo de telegram', max_length=64, blank=True, default=''
    )

    telegram_group_link = models.CharField(
        'enlace al grupo de telegram', max_length=64, blank=True, default=''
    )

    class Meta:
        verbose_name = 'año'

        ordering = ('-degree__order', 'degree', 'year',)

    def __str__(self):
        return '{} Año {}'.format(self.degree.id, self.year)


class Group(models.Model):
    '''Group of Students'''

    name = models.CharField(
        'nombre', max_length=64
    )

    number = models.IntegerField(
        'número de grupo', blank=True, null=True
    )

    year = models.ForeignKey(
        Year, models.PROTECT, 'groups',
        verbose_name='año'
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

        ordering = ('-year__degree__order', 'year__degree', 'year', 'number')

        permissions = [
            ('can_link_group', 'Puede vincular un grupo de Telegram con un grupo de alumnos')
        ]

    def __str__(self):
        return '{} {}'.format(
            self.year, self.name
        )

    def subgroups_range(self):
        return range(1, self.subgroups + 1)

    def degree(self):
        return self.year.degree


class Meeting(ModelMeta, models.Model):
    '''Assembly and commitees meetings'''

    date = models.DateTimeField('fecha')

    is_ordinary = models.BooleanField(
        'es una asamblea ordinaria', default=True
    )

    call = models.FileField(
        'convocatoria', upload_to='meetings/'
    )

    minutes = models.FileField(
        'acta', upload_to='meetings/', blank=True
    )

    minutes_approved = models.BooleanField(
        'el acta se ha aprobado', default=False
    )

    documents = models.ManyToManyField(
        DocumentMedia, verbose_name='documentos relacionados',
        blank=True
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

    order = models.IntegerField(
        'orden', default=1,
        help_text='Se ordena de forma creciente (menor número sale antes).'
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

        ordering = ('order', 'name')

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

    order = models.IntegerField(
        'orden', default=1,
        help_text='Se ordena de forma creciente (menor número sale antes).'
    )

    class Meta:
        verbose_name = 'grupo de gente importante'
        verbose_name_plural = 'grupos de gente importante'

        ordering = ('order', 'user__first_name')

    def __str__(self):
        txt = '{} en {}'.format(self.user.email, self.group)

        if self.title:
            txt += ' ({})'.format(self.title)

        return txt

    @cached_property
    def name(self):
        return self.user.get_full_name()
