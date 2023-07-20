"""Валидаторы приложения recipe."""
import re

from django.core.validators import RegexValidator


class ColorValidator(RegexValidator):
    """Валидатор цвета."""

    regex = r'^#([A-F\d]{3,6})$'
    message = 'Введенное значение не является HEX-кодом!'
    flags = re.I
