# Generated by Django 2.1.13 on 2020-08-31 10:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('code', models.IntegerField(primary_key=True, serialize=False, verbose_name='código')),
                ('name', models.CharField(max_length=64, verbose_name='nombre')),
                ('acronym', models.CharField(max_length=6, verbose_name='siglas')),
                ('quarter', models.IntegerField(choices=[(1, 'Primer cuatrimestre'), (2, 'Segundo cuatrimestre')], default=1, verbose_name='cuatrimestre')),
            ],
            options={
                'verbose_name': 'asignatura',
            },
        ),
        migrations.CreateModel(
            name='TradeOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('description', models.CharField(blank=True, default='', max_length=240, verbose_name='descripción')),
                ('is_visible', models.BooleanField(default=True, help_text='La oferta es visible para otros usuarios y puede recibir respuestas', verbose_name='es visible')),
                ('is_completed', models.BooleanField(default=False, help_text='El usuario ha completado su parte', verbose_name='proceso completado')),
            ],
            options={
                'verbose_name': 'oferta de permuta',
                'verbose_name_plural': 'ofertas de permuta',
                'ordering': ['id'],
                'permissions': [('is_manager', 'Puede ver cualquier oferta y acceder a las vistas de gestión de ofertas')],
            },
        ),
        migrations.CreateModel(
            name='TradeOfferAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groups', models.CharField(max_length=64, verbose_name='grupos ofertados')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('is_visible', models.BooleanField(default=True, help_text='La respuesta aparece en la oferta para la que fue creada.', verbose_name='es visible')),
                ('is_completed', models.BooleanField(default=False, help_text='El usuario ha completado su parte.', verbose_name='proceso completado')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='trading.TradeOffer', verbose_name='oferta')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='usuario')),
            ],
            options={
                'verbose_name': 'respuesta de oferta de permuta',
                'verbose_name_plural': 'respuestas de oferta de permuta',
            },
        ),
        migrations.CreateModel(
            name='TradeOfferLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subjects', models.CharField(max_length=64, verbose_name='asignaturas')),
                ('started', models.CharField(blank=True, default='', max_length=64, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message=None)], verbose_name='intercambios iniciados')),
                ('completed', models.CharField(blank=True, default='', max_length=64, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message=None)], verbose_name='intercambios completados')),
                ('curr_group', models.IntegerField(default=1, verbose_name='grupo actual')),
                ('curr_subgroup', models.IntegerField(default=1, verbose_name='subgrupo actual')),
                ('wanted_groups', models.CharField(default='', max_length=10, verbose_name='grupos buscados')),
                ('is_completed', models.BooleanField(default=False, help_text='Todas las asignaturas de la línea se han intercambiado.', verbose_name='proceso completado')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='trading.TradeOffer', verbose_name='oferta')),
            ],
            options={
                'verbose_name': 'línea de oferta de permuta',
                'verbose_name_plural': 'líneas de oferta de permuta',
                'ordering': ['year'],
            },
        ),
        migrations.CreateModel(
            name='TradePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='nombre')),
                ('start', models.DateTimeField(verbose_name='fecha de inicio')),
                ('end', models.DateTimeField(verbose_name='fecha de fin')),
            ],
            options={
                'verbose_name': 'periodo de intercambio',
                'verbose_name_plural': 'periodos de intercambio',
            },
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='año')),
                ('groups', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='número de grupos')),
                ('subgroups', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)], verbose_name='número de subgrupos')),
            ],
            options={
                'verbose_name': 'año',
            },
        ),
        migrations.AddField(
            model_name='tradeofferline',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='year', to='trading.Year', verbose_name='año'),
        ),
        migrations.AddField(
            model_name='tradeoffer',
            name='answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trading.TradeOfferAnswer', verbose_name='respuesta'),
        ),
        migrations.AddField(
            model_name='tradeoffer',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trading.TradePeriod', verbose_name='periodo'),
        ),
        migrations.AddField(
            model_name='tradeoffer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='usuario'),
        ),
        migrations.AddField(
            model_name='subject',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subjects', to='trading.Year', verbose_name='año'),
        ),
    ]
