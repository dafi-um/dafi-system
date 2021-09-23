from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from meta.models import ModelMeta

from heart.models import (
    DocumentMedia,
    Meeting,
)


class Topic(ModelMeta, models.Model):
    """Feedback topic.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Topic]'

    comments: 'models.Manager[Comment]'

    title: 'models.CharField[str, str]' = models.CharField(
        'nombre', max_length=200
    )

    slug: 'models.SlugField[str, str]' = models.SlugField('slug', max_length=200)

    description: 'models.TextField[str, str]' = models.TextField(
        'descripción', max_length=10000
    )

    is_public: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'permitir acceso al tema', default=True
    )

    official_position: 'models.ForeignKey[Comment, Comment]' = models.ForeignKey(
        'Comment', models.SET_NULL, 'official_position',
        verbose_name='postura oficial', blank=True, null=True
    )

    documents: 'models.ManyToManyField[None, models.Manager[DocumentMedia]]' = models.ManyToManyField(
        DocumentMedia, verbose_name='documentos relacionados',
        blank=True
    )

    meetings: 'models.ManyToManyField[None, models.Manager[Meeting]]' = models.ManyToManyField(
        Meeting, verbose_name='asambleas relacionadas',
        blank=True
    )

    created: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    updated: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de actualización', auto_now=True
    )

    _metadata = {
        'title': '__str__',
    }

    class Meta:
        verbose_name = 'tema'

        ordering = ('-updated',)

    def __str__(self) -> str:
        return f'Tema #{self.id} - {self.title}'

    def get_absolute_url(self) -> str:
        return reverse('feedback:detail', args=[self.slug])


class Comment(models.Model):
    """Feedback topic comment.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Comment]'

    topic: 'models.ForeignKey[Topic, Topic]' = models.ForeignKey(
        Topic, models.CASCADE, 'comments',
        verbose_name='tema'
    )

    text: 'models.TextField[str, str]' = models.TextField(
        'texto', max_length=5000
    )

    is_official: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es un comentario oficial', default=False
    )

    is_point: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es un punto de debate', default=False
    )

    is_anonymous: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es un comentario anónimo', default=False
    )

    author: 'models.ForeignKey[AbstractUser | None, AbstractUser | None]' = models.ForeignKey(
        get_user_model(), models.CASCADE, 'comments',
        blank=True, null=True, verbose_name='autor'
    )

    created: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de creación', auto_now_add=True
    )

    class Meta:
        verbose_name = 'comentario'

        ordering = ('-created',)

    def __str__(self) -> str:
        author: str = "comentario oficial" if self.is_official else str(self.author)

        return f'Comentario #{self.id} - Tema: {self.topic} - Autor: {author}'


class CommentVote(models.Model):
    """Feedback topic comment vote"""

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[CommentVote]'

    comment: 'models.ForeignKey[Comment, Comment]' = models.ForeignKey(
        Comment, models.CASCADE, 'votes',
        verbose_name='comentario'
    )

    user: 'models.ForeignKey[AbstractUser, AbstractUser]' = models.ForeignKey(
        get_user_model(), models.CASCADE, 'comment_votes',
        verbose_name='usuario'
    )

    is_upvote: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es voto positivo', default=True
    )

    class Meta:
        verbose_name = 'voto'

    def __str__(self) -> str:
        return f'Voto #{self.id} en Comentario #{self.comment.id}'
