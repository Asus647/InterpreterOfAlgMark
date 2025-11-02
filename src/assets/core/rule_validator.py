"""
Система проверки правил
"""

from .exceptions import RuleValidationError, CycleDetectionError
from typing import List, Tuple

class RuleValidator:
    """Проверка правил на корректность"""
    
    def __init__(self, max_rule_length: int = 1000, max_pattern_length: int = 100):
        self.max_rule_length = max_rule_length
        self.max_pattern_length = max_pattern_length
    
    def validate_rule(self, pattern: str, replacement: str, is_final: bool) -> List[str]:
        """
        Проверка одиночного правила
        
        Args:
            pattern: значение для поиска в тексте
            replacement: строка на которую нужно заменить
            is_final: терминальное ли правило
            
        Returns:
            Список ошибок, пусто если их нет
        """
        errors = []
        
        # Проверка типов
        if not isinstance(pattern, str):
            errors.append("Заменяемое значение для замены должно быть строкой")
        if not isinstance(replacement, str):
            errors.append("Значение на которое нужно заменить должно быть строкой")
        if not isinstance(is_final, bool):
            errors.append("Терминальность правила определяется значениями true или false")
        
        if errors:
            return errors
        
        # Проверка длины
        
        if len(pattern) > self.max_pattern_length:
            errors.append(f"Заменяемое значение слишком длинное ({len(pattern)} > {self.max_pattern_length})")
        
        if len(replacement) > self.max_rule_length:
            errors.append(f"Значение на которое нужно заменить слишком длинное ({len(replacement)} > {self.max_rule_length})")
        
        return errors
    
    def detect_potential_cycles(self, rules: List[Tuple[str, str, bool]]) -> List[str]:
        """
        Обнаружение потенциального зацикливания в наборе правил
        
        Args:
            rules: Список кортежей(pattern, replacement, is_final)
            
        Returns:
            Список с предупреждениями об зацикливаниях
        """
        warnings = []
        
        # Проверка на возможный бесконечный рост строки
        for i, (pattern, replacement, _) in enumerate(rules):
            if len(replacement) > len(pattern) and pattern != "":
                warnings.append(f"Правило {i+1} может вызвать бесконечный рост строки: '{pattern}'→'{replacement}'")
        
        # Проверка на взаимные замены
        for i, (pattern1, replacement1, _) in enumerate(rules):
            for j, (pattern2, replacement2, _) in enumerate(rules):
                if i != j:
                    if pattern1 in replacement2 and pattern2 in replacement1:
                        warnings.append(f"Взаимные замены между правилами {i+1} и {j+1}")
        
        return warnings