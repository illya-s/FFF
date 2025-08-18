from django import template

register = template.Library()

@register.filter
def float_dot(value, digits=1):
    try:
        return f"{float(value):.{digits}f}"
    except (ValueError, TypeError):
        return ''

@register.filter
def ms(value):
    if not value:
        return ''
    return f'{value.microsecond // 1000:03d}'