from django.db import models


class Config(models.Model):
    """Configuration entry.
    """

    MAIN_GROUP_ID = 'main_telegram_group'
    ALT_GROUP_ID = 'alt_telegram_group'

    key: 'models.CharField[str, str]' = models.CharField(
        'clave', max_length=64, primary_key=True
    )

    value: 'models.CharField[str, str]' = models.CharField(
        'valor', max_length=200
    )

    name: 'models.CharField[str, str]' = models.CharField(
        'nombre de la entrada', max_length=200
    )

    category: 'models.CharField[str | None, str | None]' = models.CharField(
        'categoría', max_length=64,
        default='', blank=True,
        help_text='Código de categoría para agrupar opciones.'
    )

    class Meta:
        verbose_name = 'entrada de configuración'
        verbose_name_plural = 'entradas de configuración'

        ordering = ('key',)

    def __str__(self) -> str:
        return f'{self.key}: {self.name}'

    @classmethod
    def get(cls, key: str) -> 'str | None':
        entry: 'Config | None' = cls.objects.filter(key=key).first()

        return entry.value if entry else None
