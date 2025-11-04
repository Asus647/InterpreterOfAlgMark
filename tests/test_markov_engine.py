"""
Юнит тестирование ядра приложения
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.markov_engine import MarkovEngine, Rule
from core.exceptions import RuleValidationError, ExecutionLimitError

class TestMarkovEngine(unittest.TestCase):
    """Тесты"""
    
    def setUp(self):
        """Настройки для тестирования"""
        self.engine = MarkovEngine(max_iterations=100)
    
    def test_add_valid_rule(self):
        """Добавление правила"""
        self.engine.add_rule('a', 'b')
        self.assertEqual(len(self.engine.rules), 1)
        self.assertEqual(self.engine.rules[0].pattern, 'a')
        self.assertEqual(self.engine.rules[0].replacement, 'b')
        self.assertFalse(self.engine.rules[0].is_final)
    
    def test_add_final_rule(self):
        """Добавление терминального правила"""
        self.engine.add_rule('a', 'b', True)
        self.assertTrue(self.engine.rules[0].is_final)
    
    def test_simple_replacement(self):
        """Простая замена текста"""
        self.engine.add_rule('cat', 'dog')
        result = self.engine.execute('I have a cat')
        self.assertEqual(result['output'], 'I have a dog')
        self.assertEqual(result['status'], 'completed')
    
    def test_final_rule_stops_execution(self):
        """Терминальное правило останавливает работу алгоритма"""
        self.engine.add_rule('a', 'b')
        self.engine.add_rule('b', 'c', True)
        self.engine.add_rule('c', 'd')
        
        result = self.engine.execute('abc')
        self.assertEqual(result['output'], 'cbc')
        self.assertEqual(result['status'], 'completed_final')
    
    def test_cycle_detection(self):
        """Обнаружение циклов"""
        self.engine.add_rule('a', 'aa')
        with self.assertRaises(ExecutionLimitError):
            self.engine.execute('a')
    
    def test_rule_ordering(self):
        """Применение правил по порядку"""
        self.engine.add_rule('a', '1')
        self.engine.add_rule('a', '2')
        
        result = self.engine.execute('aaa')
        self.assertEqual(result['output'], '111')
    
    def test_multiple_replacements(self):
        """Несколько замен за одно выполнение"""
        self.engine.add_rule('foo', 'bar')
        result = self.engine.execute('foo foo foo')
        self.assertEqual(result['output'], 'bar bar bar')
        self.assertEqual(result['statistics']['total_replacements'], 3)
    
    def test_clear_rules(self):
        """Очистка всех правил"""
        self.engine.add_rule('a', 'b')
        self.engine.add_rule('c', 'd')
        self.assertEqual(len(self.engine.rules), 2)
        
        self.engine.clear_rules()
        self.assertEqual(len(self.engine.rules), 0)

class TestRuleClass(unittest.TestCase):
    """Тесты для класса правил"""
    
    def test_rule_creation(self):
        """Создание объекта правила"""
        rule = Rule('pattern', 'replacement', True)
        self.assertEqual(rule.pattern, 'pattern')
        self.assertEqual(rule.replacement, 'replacement')
        self.assertTrue(rule.is_final)
        self.assertEqual(rule.applied_count, 0)
    
    def test_rule_string_representation(self):
        """Представление строкой"""
        rule = Rule('find', 'replace', True)
        self.assertIn('find', str(rule))
        self.assertIn('replace', str(rule))
    
    def test_rule_dict_conversion(self):
        """Преобразование из/в словарь"""
        original_rule = Rule('pattern', 'replacement', True)
        rule_dict = original_rule.to_dict()
        
        new_rule = Rule.from_dict(rule_dict)
        self.assertEqual(original_rule.pattern, new_rule.pattern)
        self.assertEqual(original_rule.replacement, new_rule.replacement)
        self.assertEqual(original_rule.is_final, new_rule.is_final)

if __name__ == '__main__':
    unittest.main()