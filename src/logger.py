import os
from datetime import datetime

# Путь к файлу логов (в директории src)
current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_dir, 'shell.log')


def get_timestamp() -> str:
    """Вернуть текущую дату и время в формате строки"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log(message: str, level: str = 'INFO') -> None:
    """Записываем сообщение в лог-файл shell.log"""
    try:
        with open(log_path, 'a', encoding='utf-8') as log_file:
            timestamp = get_timestamp()
            log_file.write(f'{timestamp} [{level}] {message}\n')
    except Exception as error:
        print(f'{get_timestamp()} ERROR: Не удалось записать лог: {error}')


def log_info(message: str) -> None:
    """Записываем информационное сообщение"""
    log(message, 'INFO')


def log_error(message: str) -> None:
    """Записываем сообщение об ошибке"""
    log(message, 'ERROR')


def log_warning(message: str) -> None:
    """Записываем предупреждение"""
    log(message, 'WARNING')