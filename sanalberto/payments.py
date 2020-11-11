import stripe

from django.urls import reverse

from main.utils import get_domain
from website import settings

stripe.api_key = settings.STRIPE_SK

def create_checkout_session(email, items, success_url, cancel_url):
    return stripe.checkout.Session.create(
        customer_email=email,
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )

def create_registration_checkout(registration):
    items = [{
      'price_data': {
        'currency': 'eur',
        'product_data': {
          'name': 'San Alberto - Inscripción para ' + registration.activity.title,
        },
        'unit_amount': 100,
      },
      'quantity': 1,
    }]

    domain = get_domain()

    success_url = domain + reverse('sanalberto:registration_paid', args=[registration.id])
    cancel_url = domain + reverse('sanalberto:registration_detail', args=[registration.id])

    return create_checkout_session(registration.user.email, items, success_url, cancel_url)

def is_checkout_paid(session_id):
    return stripe.checkout.Session.retrieve(session_id)['payment_status'] == 'paid'
