# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.html import format_html
from romani.models import UserProfile

register = Library()


@register.assignment_tag(takes_context=True)
def comandes_unread(context):
    user = user_context(context)
    if not user:
        return ''
    up = UserProfile.objects.get(user=user)
    uno = up.comandes_cistella().count()
    dos = up.contractes_cistella().count()
    total = uno + dos
    return total

def user_context(context):
    if 'user' not in context:
        return None

    request = context['request']
    user = request.user
    if user.is_anonymous():
        return None
    return user