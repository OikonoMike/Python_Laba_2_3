from typing import List, Iterator, Optional
from src.models import Task
from src.logger import log_info


class TaskQueueIterator:
    """Итератор для обхода очереди задач"""

    def __init__(self, tasks: List[Task]) -> None:
        """Инициализируем итератор с копией списка задач"""
        self._tasks = tasks
        self._index = 0

    def __iter__(self) -> 'TaskQueueIterator':
        """Возвращаем сам итератор"""
        return self

    def __next__(self) -> Task:
        """Получаем следующую задачу из очереди"""
        if self._index >= len(self._tasks):
            raise StopIteration
        task = self._tasks[self._index]
        self._index += 1
        return task


class TaskQueue:
    """Очередь задач с поддержкой итерации и фильтрации"""

    def __init__(self, max_size: Optional[int] = None) -> None:
        """Создаём пустую очередь задач"""
        self._tasks: List[Task] = []
        self._max_size = max_size
        log_info(f'Очередь создана (max_size={max_size})')

    def add(self, task: Task) -> bool:
        """Добавляем задачу в очередь"""
        if self._max_size and len(self._tasks) >= self._max_size:
            log_info(f'Очередь переполнена, задача отклонена')
            return False
        self._tasks.append(task)
        log_info(f'Задача добавлена в очередь: ID={task.id}')
        return True

    def remove(self, task_id: int) -> bool:
        """Удаляем задачу по ID из очереди"""
        for i, task in enumerate(self._tasks):
            if task.id == task_id:
                removed = self._tasks.pop(i)
                log_info(f'Задача удалена из очереди: ID={task_id}')
                return True
        log_info(f'Задача не найдена для удаления: ID={task_id}')
        return False

    def __len__(self) -> int:
        """Получаем количество задач в очереди"""
        return len(self._tasks)

    def __iter__(self) -> TaskQueueIterator:
        """Возвращаем новый итератор для обхода очереди"""
        log_info(f'Начало итерации по очереди ({len(self._tasks)} задач)')
        return TaskQueueIterator(self._tasks.copy())

    def __getitem__(self, index: int) -> Task:
        """Получаем задачу по индексу"""
        return self._tasks[index]

    def __repr__(self) -> str:
        return f'TaskQueue(size={len(self._tasks)}, max_size={self._max_size})'

    def clear(self) -> None:
        """Очищаем очередь"""
        self._tasks.clear()
        log_info('Очередь очищена')

    def is_empty(self) -> bool:
        """Проверяем, пуста ли очередь"""
        return len(self._tasks) == 0