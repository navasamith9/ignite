from django import template

register = template.Library()

@register.filter
def percentage(value, arg):
    """Calculate percentage: value / arg * 100"""
    try:
        if value and arg:
            result = (float(value) / float(arg)) * 100
            return int(result)
        return 0
    except (ValueError, ZeroDivisionError, TypeError):
        return 0