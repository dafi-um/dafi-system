# Generated by Django 2.1.13 on 2019-10-29 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('key', models.CharField(max_length=64, primary_key=True, serialize=False, verbose_name='clave')),
                ('value', models.CharField(max_length=200, verbose_name='valor')),
                ('name', models.CharField(max_length=200, verbose_name='nombre de la entrada')),
                ('category', models.CharField(blank=True, default='', help_text='Código de categoría para agrupar opciones.', max_length=64, verbose_name='categoría')),
            ],
            options={
                'verbose_name': 'entrada de configuración',
                'verbose_name_plural': 'entradas de configuración',
                'ordering': ('key',),
            },
        ),
    ]