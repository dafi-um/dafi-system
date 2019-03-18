from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    '''
    Blog Post
    '''

    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'), max_length=5000)
    pub_date = models.DateTimeField(_('date published'))

    def __str__(self):
        return self.title
