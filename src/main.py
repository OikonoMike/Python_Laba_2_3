import os
from src.models import Task
from src.sources import FileTaskSource, GeneratorTaskSource, ApiStubTaskSource
from src.collector import TaskCollector
from src.logger import log_info, log_error
from src.exceptions import TaskValidationError, TaskStateError


def create_test_file(filepath: str) -> None:
    """Создаём тестовый файл с задачами для FileTaskSource"""
    test_data = [
        '{"description": "Задача 1", "priority": 7}',
        '{"description": "Задача 2", "priority": 3}',
        '{"description": "Задача 3", "priority": 9}',
    ]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(test_data))


def main() -> None:
    """Запуск обработки задач из всех источников"""

    # Создаём сборщик
    collector = TaskCollector()

    # Добавляем источники
    collector.add_source(GeneratorTaskSource(count=3))
    collector.add_source(ApiStubTaskSource())

    # Создаём тестовый файл
    test_file = 'test_tasks.json'
    create_test_file(test_file)
    collector.add_source(FileTaskSource(test_file))

    # Тест защиты от невалидных источников
    log_info('Тест защиты от невалидных источников:')
    collector.add_source('Это строка, а не источник')
    collector.add_source(12345)

    # Собираем задачи
    log_info(f'Зарегистрировано источников: {collector.get_sources_count()}')
    tasks = collector.collect_all()

    # Вывод информации о задачах
    log_info(f'Всего собрано задач: {len(tasks)}')
    for task in tasks:
        log_info(f'  ID={task.id}, Описание={task.description}')
        log_info(f'  Приоритет={task.priority}, Статус={task.status}')
        log_info(f'  Готовность={task.is_ready}, Время={task.created_at}')

    # Тест валидации (демонстрирует работу дескрипторов)
    log_info('Тест валидации дескрипторов:')

    try:
        bad_task = Task(description='Тест', priority=15)  # Должна быть ошибка
    except TaskValidationError as e:
        log_error(f'Ожидаемая ошибка: {e}')

    try:
        bad_task = Task(description='Тест', status='invalid')  # Должна быть ошибка
    except TaskValidationError as e:
        log_error(f'Ожидаемая ошибка: {e}')

    # Тест перехода статусов
    log_info('Тест перехода статусов:')
    if tasks:
        task = tasks[0]
        log_info(f'  Начальный статус: {task.status}')
        task.start()
        log_info(f'  После start(): {task.status}')
        task.complete()
        log_info(f'  После complete(): {task.status}')

    # Очистка
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == '__main__':
    main()