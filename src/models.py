from datetime import datetime
from typing import Protocol, Iterable, runtime_checkable
from src.descriptors import (
    PriorityDescriptor,
    StatusDescriptor,
    CreatedAtDescriptor,
)
from src.exceptions import TaskValidationError, TaskStateError


class Task:
    """Задача — единица работы в платформе обработки задач"""

    # Дескрипторы для валидации
    priority = PriorityDescriptor()
    status = StatusDescriptor()
    created_at = CreatedAtDescriptor()

    def __init__(
            self,
            description: str,
            priority: int = 5,
            status: str = 'created',
    ) -> None:
        """Создаём новую задачу"""
        self._id: int = 0  # Уникальный идентификатор
        self.description = description # Описание задачи
        self.priority = priority # Приоритет задачи (по дефолту будет 5)
        self.status = status # Статус задачи
        self._created_at: datetime = datetime.now() # Время создания

    @property
    def id(self) -> int:
        """Уникальный идентификатор задачи"""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Устанавливаем ID (что может сделать только сервис)"""
        if not isinstance(value, int) or value <= 0:
            raise TaskValidationError('ID должен быть положительным целым числом')
        if self._id != 0:
            raise TaskStateError('ID можно установить только один раз')
        self._id = value

    @property
    def description(self) -> str:
        """Описание задачи"""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Устанавливаем описание задачи с валидацией"""
        if not isinstance(value, str):
            raise TaskValidationError('Описание должно быть строкой')
        if not value.strip():
            raise TaskValidationError('Описание не может быть пустым')
        self._description = value

    @property
    def is_ready(self) -> bool:
        """Проверяем, готова ли задача к запуску: создана, приоритет > 1 и описание"""
        return (self.status == 'created' and self.priority >= 1 and bool(self.description))

    def start(self) -> None:
        """Переводим задачу в статус in_progress"""
        if self.status != 'created':
            raise TaskStateError(
                f'Нельзя начать задачу со статусом {self.status}'
            )
        self.status = 'in_progress'

    def complete(self) -> None:
        """Переводим задачу в статус done"""
        if self.status != 'in_progress':
            raise TaskStateError(
                f'Нельзя завершить задачу со статусом {self.status}'
            )
        self.status = 'done'

    def fail(self) -> None:
        """Переводим задачу в статус failed"""
        if self.status in ('done', 'failed'):
            raise TaskStateError(
                f'Нельзя отменить задачу со статусом {self.status}'
            )
        self.status = 'failed'

    def __repr__(self) -> str:
        return (
            f'Task(id={self.id}, status={self.status}, '
            f'priority={self.priority}, description={self.description})'
        )


@runtime_checkable
class TaskSource(Protocol):
    """Контракт для всех источников задач"""

    def get_tasks(self) -> Iterable[Task]:
        """Получить итерируемый объект с задачами"""
        ...