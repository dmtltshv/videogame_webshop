from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def summa(queryset, field):
    return sum(getattr(obj, field) for obj in queryset)