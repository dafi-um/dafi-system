from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.urls import reverse

def get_domain():
    site_url = cache.get('main_domain')

    if not site_url:
        site_url = 'https://' + get_current_site(None).domain
        cache.set('main_domain', site_url)

    return site_url

def get_url(*args, **kwargs):
    return get_domain() + reverse(*args, **kwargs)
