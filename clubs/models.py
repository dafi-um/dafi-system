from django.contrib.auth import get_user_model
from django.db import models


class Club(models.Model):
    '''
    Club
    '''

    name = models.CharField('nombre', max_length=64)
    slug = models.SlugField('slug', max_length=64)
    description = models.TextField('descripción', max_length=300)
    telegram_group = models.CharField('grupo telegram', max_length=64, blank=True)
    telegram_channel = models.CharField('canal telegram', max_length=64, blank=True)
    manager = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               verbose_name='gestor')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'club'
        verbose_name_plural = 'clubes'

        permissions = [
            ('can_link_club', 'Puede vincular un grupo de Telegram con un club')
        ]


class ClubMeeting(models.Model):
    '''
    Club meeting
    '''

    club = models.ForeignKey(Club, on_delete=models.CASCADE, verbose_name='club', related_name='meetings')
    title = models.CharField('título', max_length=200, blank=True)
    place = models.CharField('lugar', max_length=120)
    moment = models.DateTimeField('fecha')

    def __str__(self):
        return '{} en {} ({})'.format(self.club.name, self.place, self.moment.strftime('%d %b %Y %H:%M'))

    class Meta:
        verbose_name = 'quedada'
