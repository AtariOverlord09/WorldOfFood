"""Исключения общего назначения."""


class ErrorBasic(Exception):
    """Базовый класс исключений."""

    def __init__(self, expression, message: str):
        super().__init__(message)
        self.expression = expression
        self.message = message

    def __str__(self):
        return f'{self.expression} -> {self.message}'


class AddingError(ErrorBasic):
    """Исключение, позволяющее определить ошибку добавления."""


class DeleteError(ErrorBasic):
    """Исключение, позволяющемопределить ошибку удаления."""
