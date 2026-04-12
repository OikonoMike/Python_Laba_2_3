import pytest
from datetime import datetime
from src.models import Task, TaskSource
from src.sources import GeneratorTaskSource, ApiStubTaskSource
from src.collector import TaskCollector
from src.exceptions import TaskValidationError, TaskStateError


class TestTaskDescriptors:
    """Тесты дескрипторов задачи"""

    def test_priority_valid(self) -> None:
        """Приоритет в допустимом диапазоне"""
        task = Task(description='Тест', priority=5)
        assert task.priority == 5

    def test_priority_default(self) -> None:
        """Приоритет по умолчанию = 5"""
        task = Task(description='Тест')
        assert task.priority == 5

    def test_priority_too_low(self) -> None:
        """Приоритет < 1, который вызывает ошибку"""
        with pytest.raises(TaskValidationError):
            Task(description='Тест', priority=0)

    def test_priority_too_high(self) -> None:
        """Приоритет > 10, который вызывает ошибку"""
        with pytest.raises(TaskValidationError):
            Task(description='Тест', priority=11)

    def test_priority_not_int(self) -> None:
        """Приоритет не int, который вызывает ошибку"""
        with pytest.raises(TaskValidationError):
            Task(description='Тест', priority='high')

    def test_status_valid(self) -> None:
        """Допустимый статус"""
        task = Task(description='Тест', status='in_progress')
        assert task.status == 'in_progress'

    def test_status_default(self) -> None:
        """Статус по умолчанию = created"""
        task = Task(description='Тест')
        assert task.status == 'created'

    def test_status_invalid(self) -> None:
        """Недопустимый статус , который вызывает ошибк"""
        with pytest.raises(TaskValidationError):
            Task(description='Тест', status='unknown')

    def test_created_at_automatic(self) -> None:
        """Время создания устанавливается автоматически"""
        task = Task(description='Тест')
        assert isinstance(task.created_at, datetime)

    def test_id_generated_by_service(self) -> None:
        """ID генерируется сервисом, не пользователем"""
        task = Task(description='Тест')
        assert task.id == 0  # Пока не установлен
        task.id = 1  # Может установить сервис
        assert task.id == 1

    def test_id_cannot_change(self) -> None:
        """ID нельзя изменить после установки"""
        task = Task(description='Тест')
        task.id = 1
        with pytest.raises(TaskStateError):
            task.id = 2

    def test_description_required(self) -> None:
        """Описание обязательно"""
        with pytest.raises(TaskValidationError):
            Task(description='')

    def test_description_not_string(self) -> None:
        """Описание должно быть строкой"""
        with pytest.raises(TaskValidationError):
            Task(description=123)


class TestTaskIsReady:
    """Тесты вычисляемого свойства is_ready"""

    def test_is_ready_created(self) -> None:
        """Задача со статусом created готова"""
        task = Task(description='Тест', priority=5, status='created')
        assert task.is_ready is True

    def test_is_ready_in_progress(self) -> None:
        """Задача со статусом in_progress не готова"""
        task = Task(description='Тест', status='in_progress')
        assert task.is_ready is False

    def test_is_ready_done(self) -> None:
        """Задача со статусом done не готова"""
        task = Task(description='Тест', status='done')
        assert task.is_ready is False


class TestTaskStatusTransitions:
    """Тесты перехода статусов"""

    def test_start_from_created(self) -> None:
        """Можно начать задачу из статуса created"""
        task = Task(description='Тест')
        task.start()
        assert task.status == 'in_progress'

    def test_start_from_in_progress(self) -> None:
        """Нельзя начать задачу из статуса in_progress"""
        task = Task(description='Тест')
        task.start()
        with pytest.raises(TaskStateError):
            task.start()

    def test_complete_from_in_progress(self) -> None:
        """Можно завершить задачу из статуса in_progress"""
        task = Task(description='Тест')
        task.start()
        task.complete()
        assert task.status == 'done'

    def test_complete_from_created(self) -> None:
        """Нельзя завершить задачу из статуса created"""
        task = Task(description='Тест')
        with pytest.raises(TaskStateError):
            task.complete()

    def test_fail_from_created(self) -> None:
        """Можно отменить задачу из статуса created"""
        task = Task(description='Тест')
        task.fail()
        assert task.status == 'failed'

    def test_fail_from_done(self) -> None:
        """Нельзя отменить завершённую задачу"""
        task = Task(description='Тест')
        task.start()
        task.complete()
        with pytest.raises(TaskStateError):
            task.fail()


class TestTaskCollector:
    """Тесты сборщика задач"""

    def test_collector_generates_ids(self) -> None:
        """Сборщик генерирует уникальные ID"""
        collector = TaskCollector()
        collector.add_source(GeneratorTaskSource(count=3))
        tasks = collector.collect_all()

        ids = [task.id for task in tasks]
        assert len(ids) == 3
        assert len(set(ids)) == 3  # Все ID уникальны
        assert ids == [1, 2, 3]  # Последовательные

    def test_collector_validates_source(self) -> None:
        """Сборщик проверяет контракт источника"""
        collector = TaskCollector()
        result = collector.add_source('invalid')
        assert result is False


class TestTaskSource:
    """Тесты контракта источников"""

    def test_generator_source_contract(self) -> None:
        """GeneratorSource соответствует контракту"""
        source = GeneratorTaskSource()
        assert isinstance(source, TaskSource)

    def test_api_source_contract(self) -> None:
        """ApiStubTaskSource соответствует контракту"""
        source = ApiStubTaskSource()
        assert isinstance(source, TaskSource)