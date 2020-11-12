from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from django.utils.functional import cached_property

from clubs.models import Club
from heart.models import DocumentMedia

def date_in_range(start, end):
    now = timezone.now()

    return start <= now and now < end


class Event(models.Model):
    '''
    Year event.

    Groups entities related to a specific year.
    '''

    date = models.DateField('fecha')

    selling_start = models.DateTimeField(
        'inicio de venta de productos'
    )

    selling_end = models.DateTimeField(
        'fin de venta de productos'
    )

    def __str__(self):
        return 'San Alberto de {}'.format(self.date.year)

    class Meta:
        verbose_name = 'evento'

    @cached_property
    def shop_enabled(self):
        return date_in_range(self.selling_start, self.selling_end)


class Activity(models.Model):
    '''
    Event activity
    '''

    title = models.CharField('título', max_length=120)

    description = models.TextField('descripción')

    event = models.ForeignKey(
        Event, models.CASCADE, 'activities',
        verbose_name='evento'
    )

    organiser = models.ForeignKey(
        get_user_model(), models.SET_NULL, blank=True, null=True,
        verbose_name='usuario organizador'
    )

    club = models.ForeignKey(
        Club, models.CASCADE, blank=True, null=True,
        verbose_name='club organizador'
    )

    start = models.DateTimeField('inicio')

    end = models.DateTimeField('fin')

    is_public = models.BooleanField(
        'mostrar públicamente', default=True
    )

    has_registration = models.BooleanField(
        'necesaria inscripción', default=True
    )

    registration_price = models.IntegerField(
        'precio de la inscripción', default=100,
        help_text='El precio se debe indicar en céntimos de euro (100 para 1€)'
    )

    image_1 = models.ImageField(
        'imagen 1', upload_to='activities/', null=True, blank=True
    )

    image_2 = models.ImageField(
        'imagen 2', upload_to='activities/', null=True, blank=True
    )

    documents = models.ManyToManyField(
        DocumentMedia, blank=True,
        verbose_name='documentos'
    )

    class Meta:
        verbose_name = 'actividad'
        verbose_name_plural = 'actividades'

    def __str__(self):
        return 'Actividad {}'.format(self.title)

    @cached_property
    def get_organisers(self):
        if not self.organiser and not self.club:
            return []

        return [self.organiser] if self.organiser else self.club.managers.all()

    @cached_property
    def accepts_registration(self):
        return (
            self.has_registration and
            timezone.now() < self.start + timedelta(minutes=10)
        )

    def get_user_registration(self, user):
        if not user.is_authenticated:
            return None

        return self.registrations.filter(user=user).first()


class ActivityRegistration(models.Model):
    '''Activity registration'''

    activity = models.ForeignKey(
        Activity, models.CASCADE, 'registrations',
        verbose_name='actividad'
    )

    user = models.ForeignKey(
        get_user_model(), models.CASCADE,
        verbose_name='usuario'
    )

    is_paid = models.BooleanField('pagado', default=False)

    created = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    comments = models.TextField(
        'comentarios', max_length=500, null=True, blank=True
    )

    payment_id = models.CharField(
        'ID de pago', max_length=128, null=True, blank=True
    )

    payment_error = models.CharField(
        'error del proceso de pago', max_length=256, null=True, blank=True
    )

    class Meta:
        verbose_name = 'inscripción'
        verbose_name_plural = 'inscripciones'

    def __str__(self):
        return '{} en {}'.format(self.user, self.activity)

    def get_absolute_url(self):
        return reverse('sanalberto:registration_detail', args=[self.id])


class Poll(models.Model):
    '''Designs poll'''

    event = models.ForeignKey(
        Event, models.CASCADE, 'polls',
        verbose_name='evento'
    )

    title = models.CharField('título', max_length=140)

    slug = models.SlugField(max_length=140)

    register_start = models.DateTimeField('inicio de registro')

    register_end = models.DateTimeField('fin de registro')

    voting_start = models.DateTimeField('inicio de votación')

    voting_end = models.DateTimeField('fin de votación')

    class Meta:
        verbose_name = 'encuesta'

    def __str__(self):
        return '{} ({})'.format(self.title, self.slug)

    @cached_property
    def register_enabled(self):
        return date_in_range(self.register_start, self.register_end)

    @cached_property
    def voting_enabled(self):
        return date_in_range(self.voting_start, self.voting_end)


class PollDesign(models.Model):
    '''Poll design option'''

    poll = models.ForeignKey(
        Poll, models.CASCADE, 'designs',
        verbose_name='encuesta'
    )

    user = models.ForeignKey(
        get_user_model(), models.PROTECT,
        verbose_name='creador'
    )

    title = models.CharField('título', max_length=128)

    image = models.ImageField(
        'imagen', upload_to='designs/'
    )

    source_file = models.FileField(
        'fichero fuente', upload_to='designs-sources/'
    )

    vector_file = models.FileField(
        'fichero del vectorizado', upload_to='designs-vectors/'
    )

    is_approved = models.BooleanField(
        'diseño aprobado', default=False
    )

    created = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    class Meta:
        verbose_name = 'diseño'

        ordering = ('-created', 'title')

    def __str__(self):
        return 'Diseño #{} `{}` de {}'.format(self.pk, self.title, self.user)


class Product(models.Model):
    '''Shop product'''

    cost = models.DecimalField('coste', max_digits=4, decimal_places=2)

    price = models.DecimalField('precio', max_digits=4, decimal_places=2)

    stock = models.IntegerField('stock')

    class Meta:
        verbose_name = 'producto'
