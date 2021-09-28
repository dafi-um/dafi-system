from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static
from django.utils.text import Truncator

from meta.models import ModelMeta


class Post(ModelMeta, models.Model):
    """Blog Post.
    """

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Post]'

    title: 'models.CharField[str, str]' = models.CharField(
        'título', max_length=200
    )

    slug: 'models.SlugField[str, str]' = models.SlugField(
        'slug', max_length=200
    )

    content: 'models.TextField[str, str]' = models.TextField(
        'contenido', max_length=5000
    )

    pub_date: 'models.DateTimeField[datetime, datetime]' = models.DateTimeField(
        'fecha de publicación'
    )

    author: 'models.ForeignKey[AbstractUser, AbstractUser]' = models.ForeignKey(
        get_user_model(), models.PROTECT, verbose_name='autor'
    )

    image: 'models.ImageField' = models.ImageField(
        upload_to='blog/', verbose_name='imagen', blank=True
    )

    _metadata = {
        'title': 'title',
        'description': 'get_abstract',
        'image': 'get_image'
    }

    def __str__(self) -> str:
        return f'Blog #{self.id} - {self.title}'

    def get_abstract(self) -> str:
        return Truncator(self.content).chars(200)

    def get_image(self) -> str:
        return self.image.url if self.image else static('images/favicon.png')
