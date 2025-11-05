"""
Утилиты

Пакет утилит для взаимодействия с файлами
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from ..core.markov_engine import Rule

class ProjectManager:
    """Управлят сохранением и загрузкой проектов"""
    
    def __init__(self):
        self.current_project_path = None
    
    def save_project(self, filepath: str, rules: List[Rule], 
                    input_text: str = "", output_text: str = "") -> bool:
        """
        Сохранить проект в json файл
        
        Args:
            filepath: путь для сохранения
            rules: Список правил
            input_text: Текущий введеный текст
            output_text: Текущий результат
            
        Returns:
            True если успешно, иначе False
        """
        try:
            project_data = {
                'version': '1.0',
                'metadata': {
                    'name': Path(filepath).stem,
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
            print(f"Ошибка сохранения проекта: {e}")
            return False
    
    def load_project(self, filepath: str) -> Dict[str, Any]:
        """
        Загрузить проект из json файла
        
        Args:
            filepath: путь к файлу
            
        Returns:
            Словарь с данными проекта или пустой если ошибка
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Пребразовать словари правил в объекты правил
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
            print(f"Ошибка загрузки проекта: {e}")
            return {}
    
    def export_rules_json(self, filepath: str, rules: List[Rule]) -> bool:
        """
        Экспорт правил в json файл
        
        Args:
            filepath: путь у файлу
            rules: Список правил для экспорта
            
        Returns:
            True если успешно, иначе false
        """
        try:
            rules_data = [rule.to_dict() for rule in rules]
            export_data = {
                'version': '1.0',
                'type': 'markov_rules',
                'rules_count': len(rules),
                'rules': rules_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка экспорта правил: {e}")
            return False
    
    def import_rules_json(self, filepath: str) -> List[Rule]:
        """
        Импорт правил из json файла
        
        Args:
            filepath: путь у файлу
            
        Returns:
            
        Список объектов правил или пустой список если ошибка
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            rules = []
            if 'rules' in import_data:
                rules_data = import_data['rules']
            else:
                rules_data = import_data
            
            for rule_dict in rules_data:
                rules.append(Rule.from_dict(rule_dict))
            
            return rules
            
        except Exception as e:
            print(f"Ошибка импорта правил: {e}")
            return []
    
    def get_project_info(self, filepath: str) -> Dict[str, Any]:
        """
        Получить базовую информацию о проекте без его полной загрузки
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Словарь с информацией об проекте
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            return {
                'name': project_data.get('metadata', {}).get('name', Path(filepath).stem),
                'rules_count': project_data.get('metadata', {}).get('rules_count', 0),
                'version': project_data.get('version', 'unknown'),
                'input_text_length': len(project_data.get('input_text', '')),
                'output_text_length': len(project_data.get('output_text', ''))
            }
        except Exception as e:
            print(f"Ошибка чтения информации о проекте: {e}")
            return {}
    
    def save_simple_rules(self, filepath: str, rules: List[Rule]) -> bool:
        """
        Сохраняет правила в простом формате(массив правил)
        
        Args:
            filepath: путь для сохранения файлов
            rules: Список объектов правил
            
        Returns:
            True если успешно, иначе False
        """
        try:
            rules_data = [rule.to_dict() for rule in rules]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения правил: {e}")
            return False
    
    def load_simple_rules(self, filepath: str) -> List[Rule]:
        """
        Загрузить правила из просто формата(массив правил)
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Список объектов правил
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            
            rules = []
            for rule_dict in rules_data:
                rules.append(Rule.from_dict(rule_dict))
            
            return rules
            
        except Exception as e:
            print(f"Ошибка загрузки правил: {e}")
            return []