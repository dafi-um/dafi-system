from django import template

register = template.Library()

@register.filter
def nice_name(user):
    """Returns the username of an user or its full name if is available"""

    return user.get_full_name() or user.username
