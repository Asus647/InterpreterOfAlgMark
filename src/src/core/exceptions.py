"""
Обработчики различных ошибок
"""

class MarkovError(Exception):
    """Основной обработчик ошибок"""
    pass

class RuleValidationError(MarkovError):
    """Проверка правила"""
    pass

class CycleDetectionError(MarkovError):
    """Обнаружение зацикливания"""
    pass

class ExecutionLimitError(MarkovError):
    """Превышение лимита времени выполнения"""
    pass