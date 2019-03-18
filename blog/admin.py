from django.contrib import admin

from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')
    list_filter = ['pub_date']

admin.site.register(Post, PostAdmin)
