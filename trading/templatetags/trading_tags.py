from django import template

register = template.Library()

@register.filter
def get_answer(offer, user):
    """Returns an user answer for the given offer"""

    if not user.is_authenticated:
        return None

    return offer.answers.filter(user=user).first()
