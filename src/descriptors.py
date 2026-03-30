from src.exceptions import TaskValidationError


class PriorityDescriptor:
    """Data descriptor для валидации приоритета задачи"""

    def __init__(self) -> None:
        self._name = 'priority'

    def __get__(self, instance, owner):
        """Получаем значение приоритета"""
        if instance is None:
            return self
        return instance.__dict__.get('_priority', 5)  # По дефолту будет 5

    def __set__(self, instance, value: int) -> None:
        """Устанавливаем значение приоритета с валидацией"""
        if not isinstance(value, int):
            raise TaskValidationError('Приоритет должен быть целым числом')
        if value < 1 or value > 10:
            raise TaskValidationError('Приоритет должен быть в диапазоне от 1 до 10')
        instance.__dict__['_priority'] = value


class StatusDescriptor:
    """Data descriptor для валидации статуса задачи"""

    VALID_STATUSES = ('created', 'in_progress', 'done', 'failed')  # Все валидные статусы

    def __init__(self) -> None:
        self._name = 'status'

    def __get__(self, instance, owner):
        """Получаем значение статуса"""
        if instance is None:
            return self
        return instance.__dict__.get('_status', 'created')  # По дефолту будет created

    def __set__(self, instance, value: str) -> None:
        """Устанавливаем значение статуса с валидацией"""
        if not isinstance(value, str):
            raise TaskValidationError('Статус должен быть строкой')
        if value not in self.VALID_STATUSES:
            raise TaskValidationError(f'Статус должен быть одним из: {self.VALID_STATUSES}')
        instance.__dict__['_status'] = value


class CreatedAtDescriptor:
    """Non-data descriptor для времени создания задачи"""

    def __init__(self) -> None:
        self._name = 'created_at'

    def __get__(self, instance, owner):
        """Получаем время создания"""
        if instance is None:
            return self
        return instance.__dict__.get('_created_at')

    # Тут отсутствует __set__, потому что это non-data descriptor