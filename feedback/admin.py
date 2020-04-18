from django.contrib import admin
from django.db import models

from pagedown.widgets import AdminPagedownWidget

from .models import Comment, CommentVote, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'official_position', 'created', 'updated')
    readonly_fields = ('created', 'updated')

    formfield_overrides = {
        models.TextField: {
            'widget': AdminPagedownWidget
        }
    }

    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'reputation', 'is_official')
    readonly_fields = ('created',)


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user')
