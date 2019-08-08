from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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
