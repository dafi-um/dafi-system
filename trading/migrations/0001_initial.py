# Generated by Django 2.1.7 on 2019-08-16 07:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('heart', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')),
                ('is_answer', models.BooleanField(default=False, help_text='Esta oferta es una respuesta a otra oferta', verbose_name='es una respuesta')),
                ('completed', models.BooleanField(default=False, help_text='El usuario ha completado su parte', verbose_name='proceso completado')),
                ('answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='trading.TradeOffer', verbose_name='respuesta')),
            ],
            options={
                'verbose_name': 'oferta de permuta',
                'verbose_name_plural': 'ofertas de permuta',
            },
        ),
        migrations.CreateModel(
            name='TradeOfferLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subjects', models.CharField(max_length=64, verbose_name='asignaturas')),
                ('curr_group', models.IntegerField(default=1, verbose_name='grupo actual')),
                ('curr_subgroup', models.IntegerField(default=1, verbose_name='subgrupo actual')),
                ('wanted_groups', models.CharField(default='', max_length=10, verbose_name='grupos buscados')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lines', to='trading.TradeOffer', verbose_name='oferta')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='year', to='heart.Year', verbose_name='año')),
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
        migrations.AddField(
            model_name='tradeoffer',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='trading.TradePeriod', verbose_name='periodo'),
        ),
        migrations.AddField(
            model_name='tradeoffer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='usuario'),
        ),
    ]