from django.db import models


class Config(models.Model):
    '''Configuration entry'''

    MAIN_GROUP_ID = 'main_telegram_group'
    ALT_GROUP_ID = 'alt_telegram_group'

    key = models.CharField(
        'clave', max_length=64, primary_key=True
    )

    value = models.CharField('valor', max_length=200)

    name = models.CharField(
        'nombre de la entrada', max_length=200
    )

    category = models.CharField(
        'categoría', max_length=64, default='', blank=True,
        help_text='Código de categoría para agrupar opciones.'
    )

    class Meta:
        verbose_name = 'entrada de configuración'
        verbose_name_plural = 'entradas de configuración'

        ordering = ('key',)

    def __str__(self):
        return '{}: {}'.format(self.key, self.name)

    @classmethod
    def get(cls, key):
        entry = cls.objects.filter(key=key).first()

        return entry.value if entry else None
