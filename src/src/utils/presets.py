"""
Стандартные алгоритмы встроенные в программу
"""

from typing import Dict, List, Tuple
from ..core.markov_engine import Rule

class RulePresets:
    """Коллекция предопределенных наборов правил"""
    
    @staticmethod
    def get_presets() -> Dict[str, List[Tuple[str, str, bool]]]:
        """Получение все наборов"""
        return {
            'transliteration': RulePresets.transliteration(),
            'text_normalization': RulePresets.text_normalization(),
            'html_escaping': RulePresets.html_escaping(),
            'markdown_cleanup': RulePresets.markdown_cleanup()
        }
    
    @staticmethod
    def transliteration() -> List[Tuple[str, str, bool]]:
        """Транслит кириллицы в латиницу"""
        return [
            ('а', 'a', False), ('б', 'b', False), ('в', 'v', False),
            ('г', 'g', False), ('д', 'd', False), ('е', 'e', False),
            ('ё', 'yo', False), ('ж', 'zh', False), ('з', 'z', False),
            ('и', 'i', False), ('й', 'y', False), ('к', 'k', False),
            ('л', 'l', False), ('м', 'm', False), ('н', 'n', False),
            ('о', 'o', False), ('п', 'p', False), ('р', 'r', False),
            ('с', 's', False), ('т', 't', False), ('у', 'u', False),
            ('ф', 'f', False), ('х', 'kh', False), ('ц', 'ts', False),
            ('ч', 'ch', False), ('ш', 'sh', False), ('щ', 'shch', False),
            ('ъ', '', False), ('ы', 'y', False), ('ь', '', False),
            ('э', 'e', False), ('ю', 'yu', False), ('я', 'ya', False)
        ]
    
    @staticmethod
    def text_normalization() -> List[Tuple[str, str, bool]]:
        """Нормализация и очистка текста"""
        return [
            ('  ', ' ', False),  # Множество пробелов к одному
            ('\t', ' ', False),  # Табуляции в пробелы
            (' .', '.', False),  # Удаление пробелов перед точками
            (' ,', ',', False),  # Удаление пробелов перед запятыми
            (' ;', ';', False),  # Удаление пробелов перед точками с запятыми
            (' :', ':', False),  # Удаление пробелов перед двоеточиями
            (' ?', '?', False),  # Удаление пробелов перед знаками вопросов
            (' !', '!', False),  # Удаление пробелов перед восклицательными знаками
            ('\n\n\n', '\n\n', False),  # Сокращение множеств новых строк
        ]
    
    @staticmethod
    def html_escaping() -> List[Tuple[str, str, bool]]:
        """Экранирование специальных символова HTML"""
        return [
            ('&', '&amp;', False),
            ('<', '&lt;', False),
            ('>', '&gt;', False),
            ('"', '&quot;', False),
            ("'", '&#39;', False)
        ]
    
    
    @staticmethod
    def markdown_cleanup() -> List[Tuple[str, str, bool]]:
        """Очистка текста формата Markdown"""
        return [
            ('** ', '**', False),  # Пробелы после выделеным тесктом
            (' **', '**', False),  # Пробелы перед выделенным текстом
            ('* ', '*', False),    # Пробелы после курсива
            (' *', '*', False),    # Пробелы перед курсивом
            ('__ ', '__', False),  # Пробелы после нижнего подчеркивания
            (' __', '__', False),  # Пробелы перед нижним подчеркиванием
        ]