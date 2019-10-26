# Generated by Django 2.1.13 on 2019-10-20 20:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('heart', '0006_documentmedia'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='fecha')),
                ('call', models.FileField(upload_to='meetings/', verbose_name='convocatoria')),
                ('minutes', models.FileField(upload_to='meetings/', verbose_name='acta')),
                ('absents', models.ManyToManyField(related_name='meetings_absent', to=settings.AUTH_USER_MODEL, verbose_name='ausencias justificadas')),
                ('attendees', models.ManyToManyField(related_name='meetings_attended', to=settings.AUTH_USER_MODEL, verbose_name='asistentes')),
            ],
            options={
                'verbose_name': 'asamblea de alumnos',
                'verbose_name_plural': 'asambleas de alumnos',
                'ordering': ('-date',),
            },
        ),
    ]