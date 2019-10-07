from django.db import models


class BotPermissions(models.Model):

    class Meta:
        managed = False

        default_permissions = ()
        permissions = (
            ('can_change_room_state', 'Puede cambiar el estado de una sala'),
            ('can_manage_elections', 'Puede gestionar operaciones del periodo de elecciones'),
        )
