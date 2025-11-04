"""
Полезные функции для интерпретатора

Этот пакет содержит полезные классы для файла ввода/вывода
шаблонов и остальных вспомогателей.
"""

from .file_io import ProjectManager
from .presets import RulePresets

__version__ = "1.0.0"
__all__ = [
    'ProjectManager',
    'RulePresets'
]