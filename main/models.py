from django.db import models


class Config(models.Model):
    """Configuration entry.
    """

    MAIN_GROUP_ID = 'main_telegram_group'
    ALT_GROUP_ID = 'alt_telegram_group'

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[Config]'

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


class MenuEntry(models.Model):

    id: 'models.AutoField[int, int]'

    objects: 'models.Manager[MenuEntry]'

    text: 'models.CharField[str, str]' = models.CharField(
        'texto', max_length=64,
    )

    title: 'models.CharField[str, str]' = models.CharField(
        'título', max_length=200,
        help_text='Se utilizará cómo título del enlace.',
    )

    url: 'models.CharField[str, str]' = models.CharField(
        'URL', max_length=200,
    )

    internal: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es un enlace interno', default=True,
        help_text='Los enlaces internos se pasarán al gestor de URLs de Django',
    )

    blank: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'abrir en nueva pestaña', default=False,
    )

    visible: 'models.BooleanField[bool, bool]' = models.BooleanField(
        'es visible', default=True,
    )

    order: 'models.IntegerField[int, int]' = models.IntegerField(
        'orden', default=0,
        help_text='Los enlaces se ordenarán de izquierda a derecha en orden ascendente',
    )

    class Meta:
        verbose_name = 'entrada de menú'
        verbose_name_plural = 'entradas de menú'

        ordering = ('order',)

    def __str__(self) -> str:
        return f'Entrada #{self.id}'
