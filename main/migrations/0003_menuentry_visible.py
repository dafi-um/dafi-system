# Generated by Django 3.2.7 on 2021-11-10 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_menuentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuentry',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='es visible'),
        ),
    ]
