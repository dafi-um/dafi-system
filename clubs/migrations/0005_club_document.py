# Generated by Django 2.1.13 on 2019-10-29 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0004_club_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='document',
            field=models.FileField(blank=True, help_text='Útil para bases de concursos o información de actividades.', upload_to='clubs/docs/', verbose_name='documento'),
        ),
        migrations.AddField(
            model_name='club',
            name='document_name',
            field=models.CharField(blank=True, default='', help_text='Texto que aparecerá en el enlace del documento.', max_length=120, verbose_name='nombre del documento'),
        ),
    ]
