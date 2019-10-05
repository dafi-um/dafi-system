from django.db import models


class BotPermissions(models.Model):

    class Meta:
        managed = False

        default_permissions = ()
        permissions = (
            ('can_change_room_state', 'Puede cambiar el estado de una sala'),
        )
