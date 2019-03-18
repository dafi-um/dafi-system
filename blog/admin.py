from django.contrib import admin
from django.db import models

from pagedown.widgets import AdminPagedownWidget

from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')
    list_filter = ['pub_date']

    formfield_overrides = {
        models.TextField: {
            'widget': AdminPagedownWidget
        }
    }

admin.site.register(Post, PostAdmin)
