from django import template

register = template.Library()


@register.filter
def puede_gestionar(destino, user):
    return destino.puede_gestionar(user)
