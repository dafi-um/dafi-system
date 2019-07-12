from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    '''
    Blog Post
    '''

    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, primary_key=True)
    content = models.TextField(_('content'), max_length=5000)
    pub_date = models.DateTimeField(_('date published'))
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               verbose_name=_('author'))

    def __str__(self):
        return self.title
