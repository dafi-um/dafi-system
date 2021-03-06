# Generated by Django 2.1.7 on 2019-07-19 10:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='título')),
                ('slug', models.SlugField(max_length=200, verbose_name='slug')),
                ('content', models.TextField(max_length=5000, verbose_name='contenido')),
                ('pub_date', models.DateTimeField(verbose_name='fecha de publicación')),
                ('image', models.ImageField(blank=True, upload_to='blog/', verbose_name='imagen')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='autor')),
            ],
        ),
    ]
