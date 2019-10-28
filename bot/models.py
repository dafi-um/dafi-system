from django.db import models


class BotPermissions(models.Model):

    class Meta:
        managed = False

        default_permissions = ()
        permissions = (
            ('can_change_room_state', 'Puede cambiar el estado de una sala'),
            ('can_change_alt_room_state', 'Puede cambiar el estado de la sala alternativa'),
            ('can_manage_elections', 'Puede gestionar operaciones del periodo de elecciones'),
            ('can_manage_permissions', 'Puede gestionar permisos de usuarios'),
        )
