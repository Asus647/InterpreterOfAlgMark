"""
Файл ввода/ввыода для сохранения и загрузки правил и алгоритмов
"""

import json
import pickle
from typing import Dict, Any, List
from pathlib import Path
from ..core.markov_engine import Rule

class ProjectManager:
    """Управляет сохранением и загрузкой алгоритмов"""
    
    def __init__(self):
        self.current_project_path = None
    
    def save_project(self, filepath: str, rules: List[Rule], 
                    input_text: str = "", output_text: str = "") -> bool:
        """
        Сохранить готовый алгоритм в файл
        
        Args:
            filepath: Путь для сохранения
            rules: Список правил
            input_text: Текущий введеный текст
            output_text: Текущий результат
            
        Returns:
            True если удачно, иначе False
        """
        try:
            project_data = {
                'version': '1.0',
                'metadata': {
                    'name': Path(filepath).stem,
                    'created': '',
                    'rules_count': len(rules)
                },
                'rules': [rule.to_dict() for rule in rules],
                'input_text': input_text,
                'output_text': output_text
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.current_project_path = filepath
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def load_project(self, filepath: str) -> Dict[str, Any]:
        """
        Загрузить алгоритм из файла
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Словарь с информацией об алгоритме
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Преобразует словари в объкты правил
            rules = []
            for rule_dict in project_data.get('rules', []):
                rules.append(Rule.from_dict(rule_dict))
            
            self.current_project_path = filepath
            
            return {
                'rules': rules,
                'input_text': project_data.get('input_text', ''),
                'output_text': project_data.get('output_text', '')
            }
            
        except Exception as e:
            print(f"Ошибка загрузки алгоритма: {e}")
            return {}
    
    def export_rules_json(self, filepath: str, rules: List[Rule]) -> bool:
        """Сохранение правил в json"""
        try:
            rules_data = [rule.to_dict() for rule in rules]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def import_rules_json(self, filepath: str) -> List[Rule]:
        """Загрузка из json файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            rules = []
            for rule_dict in rules_data:
                rules.append(Rule.from_dict(rule_dict))
            
            return rules
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return []