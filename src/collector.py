from typing import List, Any
from src.models import Task, TaskSource
from src.logger import log_info, log_error


class TaskCollector:
    """Сборщик задач из различных источников"""

    def __init__(self) -> None:
        """Инициализируем пустую коллекцию источников"""
        self._sources: List[TaskSource] = []
        self._next_id: int = 1  # Счётчик для генерации ID

    def add_source(self, source: Any) -> bool:
        """Добавляем новый источник в коллекцию"""
        # runtime-проверка контракта
        if not isinstance(source, TaskSource):
            log_error(f'Контракт нарушен: {type(source).__name__} не является TaskSource')
            return False

        self._sources.append(source)
        log_info(f'Источник добавлен: {type(source).__name__}')
        return True

    def _generate_id(self) -> int:
        """Генерируем уникальный ID для задачи"""
        task_id = self._next_id
        self._next_id += 1
        return task_id

    def collect_all(self) -> List[Task]:
        """Собираем все задачи из всех источников"""
        tasks: List[Task] = []
        for source in self._sources:
            log_info(f'Обработка источника: {type(source).__name__}')
            try:
                for task in source.get_tasks():
                    task.id = self._generate_id()  # Генерируем ID сервисом
                    tasks.append(task)
                    log_info(f'  Задача ID={task.id}: {task.description}')
            except Exception as e:
                log_error(f'Ошибка при получении задач: {e}')
                continue
        return tasks

    def get_sources_count(self) -> int:
        """Получаем количество зарегистрированных источников"""
        return len(self._sources)