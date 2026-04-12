import pytest
from src.models import Task
from src.queue import TaskQueue, TaskQueueIterator
from src.lazy_filters import filter_by_status, filter_by_priority, filter_by_ready, filter_combined, get_priority_stats


class TestTaskQueueIterator:
    """Тесты итератора очереди задач"""

    def test_iterator_basic(self) -> None:
        """Базовая итерация по задачам"""
        tasks = [
            Task(description='Task 1', priority=5),
            Task(description='Task 2', priority=3),
        ]
        iterator = TaskQueueIterator(tasks)

        result = list(iterator)
        assert len(result) == 2
        assert result[0].description == 'Task 1'

    def test_iterator_empty(self) -> None:
        """Итерация по пустому списку"""
        iterator = TaskQueueIterator([])
        result = list(iterator)
        assert len(result) == 0

    def test_iterator_stopiteration(self) -> None:
        """StopIteration при завершении итерации"""
        tasks = [Task(description='Single')]
        iterator = TaskQueueIterator(tasks)

        next(iterator)
        with pytest.raises(StopIteration):
            next(iterator)


class TestTaskQueue:
    """Тесты очереди задач"""

    def test_queue_create_empty(self) -> None:
        """Создание пустой очереди"""
        queue = TaskQueue()
        assert len(queue) == 0
        assert queue.is_empty() is True

    def test_queue_add_task(self) -> None:
        """Добавление задачи в очередь"""
        queue = TaskQueue()
        task = Task(description='Test task')
        result = queue.add(task)

        assert result is True
        assert len(queue) == 1
        assert queue.is_empty() is False

    def test_queue_add_with_max_size(self) -> None:
        """Добавление задачи при заполненной очереди"""
        queue = TaskQueue(max_size=2)
        queue.add(Task(description='Task 1'))
        queue.add(Task(description='Task 2'))
        result = queue.add(Task(description='Task 3'))

        assert result is False
        assert len(queue) == 2

    def test_queue_remove_task(self) -> None:
        """Удаление задачи по ID"""
        queue = TaskQueue()
        task = Task(description='Test')
        task.id = 1
        queue.add(task)

        result = queue.remove(1)
        assert result is True
        assert len(queue) == 0

    def test_queue_remove_not_found(self) -> None:
        """Удаление несуществующей задачи"""
        queue = TaskQueue()
        result = queue.remove(999)
        assert result is False

    def test_queue_iteration(self) -> None:
        """Итерация по очереди"""
        queue = TaskQueue()
        for i in range(3):
            task = Task(description=f'Task {i}')
            task.id = i + 1
            queue.add(task)

        descriptions = [t.description for t in queue]
        assert descriptions == ['Task 0', 'Task 1', 'Task 2']

    def test_queue_repeated_iteration(self) -> None:
        """Повторная итерация по очереди"""
        queue = TaskQueue()
        queue.add(Task(description='Task A'))
        queue.add(Task(description='Task B'))

        # Первая итерация
        first = [t.description for t in queue]
        # Вторая итерация
        second = [t.description for t in queue]

        assert first == second
        assert len(first) == 2

    def test_queue_getitem(self) -> None:
        """Доступ по индексу"""
        queue = TaskQueue()
        task = Task(description='Indexed task')
        queue.add(task)

        assert queue[0].description == 'Indexed task'

    def test_queue_clear(self) -> None:
        """Очистка очереди"""
        queue = TaskQueue()
        queue.add(Task(description='To clear'))
        queue.clear()

        assert len(queue) == 0
        assert queue.is_empty() is True

    def test_queue_repr(self) -> None:
        """Строковое представление"""
        queue = TaskQueue(max_size=10)
        queue.add(Task(description='Test'))

        assert 'TaskQueue' in repr(queue)
        assert 'size=1' in repr(queue)


class TestFilters:
    """Тесты ленивых фильтров"""

    @pytest.fixture
    def sample_tasks(self) -> list:
        """Набор тестовых задач"""
        tasks = []
        for i in range(5):
            task = Task(description=f'Task {i}', priority=i + 1)
            task.id = i + 1
            tasks.append(task)
        # Меняем статусы для тестов
        tasks[0].status = 'created' # В очереди
        tasks[1].status = 'created' # В очереди (намеренно дублирую для теста)
        tasks[2].status = 'in_progress' # В работе
        tasks[3].status = 'done' # Готовые
        tasks[4].status = 'failed'
        return tasks

    def test_filter_by_status(self, sample_tasks) -> None:
        """Фильтр по статусу"""
        result = list(filter_by_status(sample_tasks, 'created'))
        assert len(result) == 2
        assert all(t.status == 'created' for t in result)

    def test_filter_by_status_no_matches(self, sample_tasks) -> None:
        """Фильтр без совпадений"""
        result = list(filter_by_status(sample_tasks, 'unknown'))
        assert len(result) == 0

    def test_filter_by_priority_min(self, sample_tasks) -> None:
        """Фильтр по минимальному приоритету"""
        result = list(filter_by_priority(sample_tasks, min_priority=3))
        assert len(result) == 3
        assert all(t.priority >= 3 for t in result)

    def test_filter_by_priority_range(self, sample_tasks) -> None:
        """Фильтр по диапазону приоритетов"""
        result = list(
            filter_by_priority(sample_tasks, min_priority=2, max_priority=4)
        )
        assert len(result) == 3
        for t in result:
            assert 2 <= t.priority <= 4

    def test_filter_by_ready(self, sample_tasks) -> None:
        """Фильтр готовых задач"""
        result = list(filter_by_ready(sample_tasks))
        # Только задачи со статусом 'created' и priority >= 1
        assert all(t.is_ready for t in result)

    def test_filter_combined(self, sample_tasks) -> None:
        """Комбинированный фильтр"""
        result = list(
            filter_combined(
                sample_tasks,
                status='created',
                min_priority=1,
                max_priority=5
            )
        )
        assert len(result) == 2
        for t in result:
            assert t.status == 'created'

    def test_filter_combined_no_criteria(self, sample_tasks) -> None:
        """Комбинированный фильтр без критериев"""
        result = list(filter_combined(sample_tasks))
        assert len(result) == len(sample_tasks)

    def test_get_priority_stats(self, sample_tasks) -> None:
        """Статистика по приоритетам"""
        stats = list(get_priority_stats(sample_tasks))
        assert len(stats) == 5  # 5 разных приоритетов
        assert (1, 1) in stats
        assert (5, 1) in stats

    def test_filter_is_lazy(self, sample_tasks) -> None:
        """Проверка ленивости фильтра (возвращает генератор)"""
        result = filter_by_status(sample_tasks, 'created')
        # Генератор не вычисляется пока не итерируем
        assert hasattr(result, '__next__')
        assert hasattr(result, '__iter__')


class TestIntegration:
    """Интеграционные тесты очереди и фильтров"""

    def test_queue_with_filters(self) -> None:
        """Очередь с применением фильтров"""
        queue = TaskQueue()
        for i in range(10):
            task = Task(description=f'Task {i}', priority=i + 1)
            task.id = i + 1
            if i < 5:
                task.status = 'created'
            else:
                task.status = 'done'
            queue.add(task)

        # Фильтруем задачи в очереди
        created_tasks = list(filter_by_status(queue, 'created'))
        assert len(created_tasks) == 5

    def test_queue_iteration_with_modification(self) -> None:
        """Итерация не влияет на исходную очередь"""
        queue = TaskQueue()
        queue.add(Task(description='Original'))

        # Итерируем
        list(queue)

        # Очередь не изменилась
        assert len(queue) == 1