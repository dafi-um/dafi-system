from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

_site_url = 'https://' + get_current_site(None).domain

def get_domain():
    return _site_url

def get_url(*args, **kwargs):
    return _site_url + reverse(*args, **kwargs)
