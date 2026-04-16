from django import template

register = template.Library()

@register.filter
def average_rating(reviews):
    if not reviews:
        return 0
    return sum(review.rating for review in reviews) / len(reviews)

@register.filter
def lookup(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def mul(value, arg):
    return value * arg

@register.filter
def div(value, arg):
    try:
        return value / arg
    except (ValueError, ZeroDivisionError):
        return 0
