"""
Основное ядро алгоритмов Маркова
"""

from typing import List, Tuple, Dict, Any
from .rule_validator import RuleValidator
from .exceptions import CycleDetectionError, ExecutionLimitError, RuleValidationError

class Rule:
    """Представляет одиночное правило"""
    
    def __init__(self, pattern: str, replacement: str, is_final: bool = False):
        self.pattern = pattern
        self.replacement = replacement
        self.is_final = is_final
        self.applied_count = 0
    
    def __str__(self) -> str:
        final_mark = " ·" if self.is_final else ""
        return f"'{self.pattern}' → '{self.replacement}'{final_mark}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует правило в словарь"""
        return {
            'pattern': self.pattern,
            'replacement': self.replacement,
            'is_final': self.is_final
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        """Содает правило из словаря"""
        return cls(data['pattern'], data['replacement'], data.get('is_final', False))

class ExecutionHistory:
    """Отслеживает историю выполнения правил"""
    
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
    
    def add_entry(self, iteration: int, rule: Rule, position: int, 
                  before: str, after: str) -> None:
        """Добавляет выполняемое вхождение"""
        self.entries.append({
            'iteration': iteration,
            'rule_pattern': rule.pattern,
            'rule_replacement': rule.replacement,
            'is_final': rule.is_final,
            'position': position,
            'before': before,
            'after': after,
            'rule_applied_count': rule.applied_count
        })
    
    def clear(self) -> None:
        """Очистить историю"""
        self.entries.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику выполнения"""
        if not self.entries:
            return {}
        
        return {
            'total_steps': len(self.entries),
            'final_rule_applied': any(entry['is_final'] for entry in self.entries),
            'unique_rules_applied': len(set(entry['rule_pattern'] for entry in self.entries))
        }

class MarkovEngine:
    """
    Основное ядро интерпретатора правил алгоритмов Маркова
    """
    
    def __init__(self, max_iterations: int = 1000, max_output_length: int = 10000):
        self.rules: List[Rule] = []
        self.validator = RuleValidator()
        self.history = ExecutionHistory()
        self.max_iterations = max_iterations
        self.max_output_length = max_output_length
        
        # Статистика выполнения
        self.reset_stats()
    
    def reset_stats(self) -> None:
        """Сбросить статистику"""
        self.stats = {
            'total_executions': 0,
            'total_replacements': 0,
            'total_cycles_detected': 0
        }
    
    def add_rule(self, pattern: str, replacement: str, is_final: bool = False) -> None:
        """
        Добавление нового правила с проверкой
        
        Args:
            pattern: Заменяемое значение для поиска в тексте
            replacement: Значение на которое нужно заменить
            is_final: терминально ли правило
            
        Raises:
            RuleValidationError: Если правило не прошло проверку
        """
        errors = self.validator.validate_rule(pattern, replacement, is_final)
        if errors:
            raise RuleValidationError(f"Недействительное правило: {', '.join(errors)}")
        
        self.rules.append(Rule(pattern, replacement, is_final))
    
    def clear_rules(self) -> None:
        """Очистить все правила"""
        self.rules.clear()
    
    def validate_rule_set(self) -> List[str]:
        """Проверить весь набор правил"""
        warnings = []
        
        # Преобразование в кортеж для проверки
        rule_tuples = [(rule.pattern, rule.replacement, rule.is_final) for rule in self.rules]
        warnings.extend(self.validator.detect_potential_cycles(rule_tuples))
        
        return warnings
    
    def execute(self, input_text: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Выполнить алгоритм Маркова на введеном тексте
        
        Args:
            input_text: Вводимый текст
            verbose: Предоставлять ли подробный вывод
            
        Returns:
            Словарь с результатами выполнения
        """
        # Сброс для нового выполнеия
        self.history.clear()
        for rule in self.rules:
            rule.applied_count = 0
        
        work_string = input_text
        iteration = 0
        self.stats['total_executions'] += 1
        
        # Предвыполняемае проверка
        warnings = self.validate_rule_set()
        if warnings and verbose:
            print("Обнарудены потенциальные проблемы:", warnings)
        
        # Основной цикл исполнения
        while iteration < self.max_iterations:
            iteration += 1
            applied_this_iteration = False
            
            for rule in self.rules:
                position = work_string.find(rule.pattern)
                
                if position != -1:
                    # Применение правила
                    before = work_string
                    work_string = (work_string[:position] + 
                                 rule.replacement + 
                                 work_string[position + len(rule.pattern):])
                    
                    # Обновление статистики
                    rule.applied_count += 1
                    self.stats['total_replacements'] += 1
                    applied_this_iteration = True
                    
                    # Запись в историю
                    self.history.add_entry(iteration, rule, position, before, work_string)
                    
                    # Проверка на длину выводимого значения
                    if len(work_string) > self.max_output_length:
                        raise ExecutionLimitError(
                            f"Достигнут лимит результата: {len(work_string)} > {self.max_output_length}"
                        )
                    
                    # Проверка на терминальное правило
                    if rule.is_final:
                        return self._build_result(work_string, "completed_final", iteration, warnings)
                    
                    # Возврат к первому правилу
                    break
            
            if not applied_this_iteration:
                # Если ни одно правило не применилось - завершение работы алгоритма
                return self._build_result(work_string, "completed", iteration, warnings)
        
        # Достигнут лимит итераций
        self.stats['total_cycles_detected'] += 1
        raise ExecutionLimitError(
            f"Достигнут максимум итераций: {self.max_iterations}"
        )
    
    def _build_result(self, output: str, status: str, iterations: int, 
                     warnings: List[str]) -> Dict[str, Any]:
        """Построение словаря результатов"""
        history_stats = self.history.get_stats()
        
        return {
            'output': output,
            'status': status,
            'iterations': iterations,
            'warnings': warnings,
            'statistics': {
                **self.stats,
                **history_stats,
                'rules_count': len(self.rules),
                'active_rules_count': sum(1 for rule in self.rules if rule.applied_count > 0)
            },
            'history': self.history.entries[:],  # Copy of history
            'rule_usage': [
                {
                    'pattern': rule.pattern,
                    'replacement': rule.replacement,
                    'is_final': rule.is_final,
                    'applied_count': rule.applied_count
                }
                for rule in self.rules
            ]
        }
    
    def save_rules(self, filepath: str) -> None:
        """Сохранение правил в json"""
        import json
        rules_data = [rule.to_dict() for rule in self.rules]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f, indent=2, ensure_ascii=False)
    
    def load_rules(self, filepath: str) -> None:
        """Загрузка правил из json"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        self.clear_rules()
        for rule_data in rules_data:
            self.rules.append(Rule.from_dict(rule_data))