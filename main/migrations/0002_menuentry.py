# Generated by Django 3.2.7 on 2021-11-10 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=64, verbose_name='texto')),
                ('title', models.CharField(help_text='Se utilizará cómo título del enlace.', max_length=200, verbose_name='título')),
                ('url', models.CharField(max_length=200, verbose_name='URL')),
                ('internal', models.BooleanField(default=True, help_text='Los enlaces internos se pasarán al gestor de URLs de Django', verbose_name='es un enlace interno')),
                ('blank', models.BooleanField(default=False, verbose_name='abrir en nueva pestaña')),
                ('order', models.IntegerField(default=0, help_text='Los enlaces se ordenarán de izquierda a derecha en orden ascendente', verbose_name='orden')),
            ],
            options={
                'verbose_name': 'entrada de menú',
                'verbose_name_plural': 'entradas de menú',
                'ordering': ('order',),
            },
        ),
    ]