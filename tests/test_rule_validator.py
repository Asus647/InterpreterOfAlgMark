"""
Юнит тесты для системы проверки правил
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.rule_validator import RuleValidator

class TestRuleValidator(unittest.TestCase):
    """Тесты"""
    
    def setUp(self):
        self.validator = RuleValidator()
    
    def test_valid_rule(self):
        """Проверка правила"""
        errors = self.validator.validate_rule('pattern', 'replacement', False)
        self.assertEqual(len(errors), 0)
    
    def test_cycle_detection(self):
        """Обнаружение цикла в наборе правил"""
        rules = [
            ('a', 'ba', False),
            ('b', 'a', False)
        ]
        
        warnings = self.validator.detect_potential_cycles(rules)
        self.assertGreater(len(warnings), 0)
    
    def test_pattern_too_long(self):
        """Слишком большая длина заменяемого"""
        long_pattern = 'a' * 101  # Exceeds default 100 char limit
        errors = self.validator.validate_rule(long_pattern, 'replacement', False)
        self.assertGreater(len(errors), 0)
        self.assertIn('заменяемое значение слишком длинное (101 > 100)', errors[0].lower())

if __name__ == '__main__':
    unittest.main()