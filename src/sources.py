import json
import random
from typing import List, Iterable
from src.models import Task


class FileTaskSource:
    """Источник задач из файла"""

    def __init__(self, filepath: str) -> None:
        """Создаём источник с указанным файлом"""
        self.filepath = filepath

    def get_tasks(self) -> List[Task]:
        """Считаем задачи из файла"""
        tasks = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                tasks.append(
                    Task(
                        description=data.get('description', 'Без описания'),
                        priority=data.get('priority', 5),
                    )
                )
        return tasks


class GeneratorTaskSource:
    """Источник задач из генератора"""

    def __init__(self, count: int = 5) -> None:
        """Создаём новый источник с указанным количеством задач"""
        if count < 0:
            raise ValueError('Количество задач не может быть отрицательным')
        self.count = count

    def get_tasks(self) -> Iterable[Task]:
        """Генерируем указанное количество задач"""
        for i in range(self.count):
            yield Task(
                description=f'Сгенерированная задача #{i}',
                priority=random.randint(1, 10),
            )


class ApiStubTaskSource:
    """Источник задач из API-заглушки"""

    def __init__(self, endpoint: str = 'https://api.example.com/tasks') -> None:
        """Создаём новый источник с указанным endpoint"""
        self.endpoint = endpoint

    def get_tasks(self) -> List[Task]:
        """Получаем задачи из API-заглушки"""
        return [
            Task(description='Обработать заказ', priority=8),
            Task(description='Отправить уведомление', priority=5),
            Task(description='Проверить статистику', priority=3),
        ]