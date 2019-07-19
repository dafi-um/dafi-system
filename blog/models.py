from django.contrib.auth import get_user_model
from django.db import models


class Post(models.Model):
    '''
    Blog Post
    '''

    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', max_length=200)
    content = models.TextField('contenido', max_length=5000)
    pub_date = models.DateTimeField('fecha de publicación')
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.PROTECT,
                               verbose_name='autor')
    image = models.ImageField(upload_to='blog/', verbose_name='imagen', blank=True)

    def __str__(self):
        return self.title
