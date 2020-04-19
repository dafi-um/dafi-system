from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from meta.models import ModelMeta

from heart.models import DocumentMedia, Meeting


class Topic(ModelMeta, models.Model):
    '''Feedback topic'''

    title = models.CharField(
        'nombre', max_length=200
    )

    slug = models.SlugField('slug', max_length=200)

    description = models.TextField(
        'descripción', max_length=10000
    )

    is_public = models.BooleanField(
        'permitir acceso al tema', default=True
    )

    official_position = models.ForeignKey(
        'Comment', models.SET_NULL, 'official_position',
        verbose_name='postura oficial', blank=True, null=True
    )

    documents = models.ManyToManyField(
        DocumentMedia, verbose_name='documentos relacionados',
        blank=True
    )

    meetings = models.ManyToManyField(
        Meeting, verbose_name='asambleas relacionadas',
        blank=True
    )

    created = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    updated = models.DateTimeField(
        'fecha de actualización', auto_now=True
    )

    _metadata = {
        'title': '__str__',
    }

    class Meta:
        verbose_name = 'tema'

        ordering = ('-updated',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('feedback:detail', args=[self.slug])


class Comment(models.Model):
    '''Feedback topic comment'''

    topic = models.ForeignKey(
        Topic, models.CASCADE, 'comments',
        verbose_name='tema'
    )

    text = models.TextField(
        'texto', max_length=5000
    )

    is_official = models.BooleanField(
        'es un comentario oficial', default=False
    )

    is_point = models.BooleanField(
        'es un punto de debate', default=False
    )

    is_anonymous = models.BooleanField(
        'es un comentario anónimo', default=False
    )

    author = models.ForeignKey(
        get_user_model(), models.CASCADE, 'comments',
        blank=True, null=True, verbose_name='autor'
    )

    created = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    class Meta:
        verbose_name = 'comentario'

        ordering = ('-created',)

    def __str__(self):
        if self.is_official:
            return '#{} OFICIAL en {}'.format(self.id, self.topic)
        else:
            return '#{} {} en {}'.format(self.id, self.author, self.topic)


class CommentVote(models.Model):
    '''Feedback topic comment vote'''

    comment = models.ForeignKey(
        Comment, models.CASCADE, 'votes',
        verbose_name='comentario'
    )

    user = models.ForeignKey(
        get_user_model(), models.CASCADE, 'comment_votes',
        verbose_name='usuario'
    )

    is_upvote = models.BooleanField(
        'es voto positivo', default=True
    )

    class Meta:
        verbose_name = 'voto'
