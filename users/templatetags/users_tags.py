from hashlib import md5
from urllib.parse import urlencode

from django import template
from django.utils.safestring import mark_safe

SECURE_GRAVATAR_URL = 'https://secure.gravatar.com'
DEFAULT_GRAVATAR_STYLE = 'mm'

register = template.Library()

@register.filter
def nice_name(user):
    '''Returns the username of an user or its full name if is available'''

    return user.get_full_name() or user.username

@register.filter
def gravatar(user_or_email, size=150):
    '''Returns a gravatar URL given its email'''

    if hasattr(user_or_email, 'email'):
        email = user_or_email.email
    else:
        email = user_or_email

    email = email.strip().lower().encode('utf-8')

    return '{}/avatar/{}?{}'.format(
        SECURE_GRAVATAR_URL,
        md5(email).hexdigest(),
        urlencode({'s': str(size), 'd': DEFAULT_GRAVATAR_STYLE})
    )
