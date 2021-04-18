from django.contrib.auth import get_user_model
from django.templatetags.static import static
from django.db import models
from django.utils.text import Truncator

from meta.models import ModelMeta


class Post(ModelMeta, models.Model):
    '''
    Blog Post
    '''

    title = models.CharField('título', max_length=200)

    slug = models.SlugField('slug', max_length=200)

    content = models.TextField('contenido', max_length=5000)

    pub_date = models.DateTimeField('fecha de publicación')

    author = models.ForeignKey(
        get_user_model(), models.PROTECT, verbose_name='autor'
    )

    image = models.ImageField(
        upload_to='blog/', verbose_name='imagen', blank=True
    )

    _metadata = {
        'title': 'title',
        'description': 'get_abstract',
        'image': 'get_image'
    }

    def __str__(self):
        return self.title

    def get_abstract(self):
        return Truncator(self.content).chars(200)

    def get_image(self):
        return self.image.url if self.image else static('images/favicon.png')
