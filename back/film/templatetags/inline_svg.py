from django import template
from django.utils.safestring import mark_safe
import os

register = template.Library()

@register.simple_tag
def svg(path):
    full_path = os.path.join('static', path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return mark_safe(f.read())
    except FileNotFoundError:
        return f'<!-- SVG not found: {path} -->'
