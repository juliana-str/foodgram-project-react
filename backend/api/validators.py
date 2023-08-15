import re

from django.core.exceptions import ValidationError

REGEX_USERNAME = re.compile(r'^[\w.@+-]+\w')
REGEX_SLUG = re.compile(r'^[-a-zA-Z0-9_]+$')


def validate_username(value):
    if not REGEX_USERNAME.fullmatch(value):
        raise ValidationError(
            'Можно использовать только буквы, цифры и символы @.+-_".')
    return value


def validate_slug(value):
    if not REGEX_SLUG.fullmatch(value):
        raise ValidationError(
            'Можно использовать только буквы, цифры')
    return value


def validate_amount(value):
    if value < 1:
        raise ValidationError('Количество продукта должно быть больше 0')
    return value


def validate_ingredients(value):
    if len(value) < 1:
        raise ValidationError('Нужно добавить ингредиент!')
    return value

def validate_time(value):
    if value < 1:
        raise ValidationError(
            'Время приготовления не может быть меньше 1 минуты')
    return value
