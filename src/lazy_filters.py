from typing import Generator, Optional, Iterable
from src.models import Task


def filter_by_status(
        tasks: Iterable[Task],
        status: str
) -> Generator[Task, None, None]:
    """Фильтр задач по статусу"""
    for task in tasks:
        if task.status == status:
            yield task


def filter_by_priority(
        tasks: Iterable[Task],
        min_priority: int,
        max_priority: Optional[int] = None
) -> Generator[Task, None, None]:
    """Фильтр задач по приоритету"""
    for task in tasks:
        if task.priority >= min_priority:
            if max_priority is None or task.priority <= max_priority:
                yield task


def filter_by_ready(
        tasks: Iterable[Task]
) -> Generator[Task, None, None]:
    """Фильтр задач, готовых к выполнению"""
    for task in tasks:
        if task.is_ready:
            yield task


def filter_combined(
        tasks: Iterable[Task],
        status: Optional[str] = None,
        min_priority: Optional[int] = None,
        max_priority: Optional[int] = None
) -> Generator[Task, None, None]:
    """Комбинационный фильтр по нескольким критериям"""
    for task in tasks:
        # Проверка статуса
        if status and task.status != status:
            continue
        # Проверка приоритета
        if min_priority and task.priority < min_priority:
            continue
        if max_priority and task.priority > max_priority:
            continue
        yield task


def get_priority_stats(
        tasks: Iterable[Task]
) -> Generator[tuple, None, None]:
    """Генератор статистики по приоритетам (приоритет, количество)"""
    priority_counts = {}
    for task in tasks:
        p = task.priority
        priority_counts[p] = priority_counts.get(p, 0) + 1

    for priority, count in sorted(priority_counts.items()):
        yield (priority, count)