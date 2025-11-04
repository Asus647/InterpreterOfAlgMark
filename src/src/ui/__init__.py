"""
Компоненты ПИ для интерпретатора

Этот пакет содержит все компоненты графического пользовательского интерфейса
для построения проекта на фреймфорке Flet.
"""

from .main_window import MarkovApp, main
from .rule_editor import RuleEditor
from .history_viewer import HistoryViewer

__version__ = "1.0.0"
__all__ = [
    'MarkovApp',
    'main', 
    'RuleEditor',
    'HistoryViewer'
]