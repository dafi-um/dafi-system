# Generated by Django 3.2.7 on 2021-10-17 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanalberto', '0014_polls_winner_tshirts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='polldesign',
            name='voting_image',
            field=models.ImageField(blank=True, help_text='Esta imagen se mostrará solamente en el formulario de votación', upload_to='designs-tshirts/', verbose_name='imagen de votación'),
        ),
    ]
