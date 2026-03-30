class TaskError(Exception):
    """Базовое исключение для ошибок задачи"""
    pass


class TaskValidationError(TaskError):
    """Исключение при нарушении валидации атрибутов задачи"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f'Ошибка валидации: {message}')


class TaskStateError(TaskError):
    """Исключение при некорректном изменении состояния задачи"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f'Ошибка состояния: {message}')