from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Subject(models.Model):
    '''
    Academic subject
    '''

    QUARTERS = [
        (1, 'Primer cuatrimestre'),
        (2, 'Segundo cuatrimestre'),
    ]

    code = models.IntegerField('código', primary_key=True)
    name = models.CharField('nombre', max_length=64)
    acronym = models.CharField('siglas', max_length=6)
    quarter = models.IntegerField('cuatrimestre', choices=QUARTERS, default=1)
    year = models.IntegerField('año', validators=[MinValueValidator(1), MaxValueValidator(4)])
    groups = models.IntegerField('número de grupos', validators=[MinValueValidator(1), MaxValueValidator(4)])

    def __str__(self):
        return '{} {} ({})'.format(self.code, self.name, self.acronym)

    class Meta:
        verbose_name = 'asignatura'


class Room(models.Model):
    name = models.CharField('nombre de la sala', max_length=64)
    code = models.CharField('código de la sala', max_length=64, unique=True)
    members = models.CharField('miembros en la sala', max_length=128, blank=True, default='')

    def _get_members_list(self):
        if not self.members:
            return []

        return [int(x) for x in self.members.split(',')]

    def _set_members_list(self, l):
        self.members = ','.join(str(x) for x in l)

    def get_members(self):
        return User.objects.filter(pk__in=self._get_members_list())

    def add_member(self, user):
        if not isinstance(user, User):
            raise TypeError('Must provide a valid user instance')

        l = self._get_members_list()

        if user.id in l:
            return

        l.append(user.id)

        self._set_members_list(l)
        self.save()

    def remove_member(self, user):
        if not isinstance(user, User):
            raise TypeError('Must provide a valid user instance')

        l = self._get_members_list()

        if user.id not in l:
            return

        l.remove(user.id)

        self._set_members_list(l)
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'sala'
