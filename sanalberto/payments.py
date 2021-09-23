from django.urls import reverse

import stripe
from stripe.api_resources.checkout import Session

from main.utils import get_domain
from website import settings

from .models import ActivityRegistration


stripe.api_key = settings.STRIPE_SK


def create_checkout_session(email: str, items: list[dict], success_url: str, cancel_url: str) -> Session:
    return stripe.checkout.Session.create(
        customer_email=email,
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )


def create_registration_checkout(registration: ActivityRegistration) -> Session:
    items = [{
        'price_data': {
            'currency': 'eur',
            'product_data': {
                'name': 'San Alberto - Inscripción para ' + registration.activity.title,
            },
            'unit_amount': registration.activity.registration_price,
        },
        'quantity': 1,
    }]

    domain = get_domain()

    success_url = domain + reverse('sanalberto:registration_paid', args=[registration.id])
    cancel_url = domain + reverse('sanalberto:registration_detail', args=[registration.id])

    return create_checkout_session(registration.user.email, items, success_url, cancel_url)


def is_checkout_paid(session_id) -> bool:
    return stripe.checkout.Session.retrieve(session_id)['payment_status'] == 'paid'
