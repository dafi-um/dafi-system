from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=5000)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title
