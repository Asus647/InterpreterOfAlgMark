"""
Компонент просмотра истории выполнения
"""

import flet as ft
from typing import List, Dict, Any

class HistoryViewer:
    """Компонент для просмотра истории выполнения"""
    
    def __init__(self):
        self.history_data = []
        self._create_components()
    
    def _create_components(self):
        """Создание пользовательского интерфейса"""
        self.history_list = ft.ListView(expand=True)
        
        self.stats_text = ft.Text("", size=14)
        
        self.clear_button = ft.ElevatedButton(
            "Очистить историю",
            icon="clear_all",
            on_click=self._clear_history
        )
    
    def set_history(self, history_data: List[Dict[str, Any]], stats: Dict[str, Any]):
        """Установить данные истории для отображения"""
        self.history_data = history_data
        self._refresh_display(stats)
    
    def _refresh_display(self, stats: Dict[str, Any]):
        """Обновить отображаемую историю"""
        # Обновить статистику
        stats_text = self._format_stats(stats)
        self.stats_text.value = stats_text
        self.stats_text.update()
        
        # Обновить список истории
        self.history_list.controls.clear()
        
        if not self.history_data:
            self.history_list.controls.append(
                ft.Text("Нет доступной истории выполнения", style="bodyMedium")
            )
        else:
            for entry in self.history_data[-50:]:  # Показывать последние 50 вхождений правил
                history_card = self._create_history_card(entry)
                self.history_list.controls.append(history_card)
        
        self.history_list.update()
    
    def _format_stats(self, stats: Dict[str, Any]) -> str:
        """Формат отображения статистики"""
        if not stats:
            return "Нет доступной статистики"
        
        lines = ["Статистика выполнений:"]
        
        if 'iterations' in stats:
            lines.append(f"• Итерации: {stats['iterations']}")
        if 'total_replacements' in stats:
            lines.append(f"• Всего замен: {stats['total_replacements']}")
        if 'rules_count' in stats:
            lines.append(f"• Всего правил: {stats['rules_count']}")
        if 'active_rules_count' in stats:
            lines.append(f"• Активные правила: {stats['active_rules_count']}")
        if 'status' in stats:
            lines.append(f"• Статус: {stats['status']}")
        
        return "\n".join(lines)
    
    def _create_history_card(self, entry: Dict[str, Any]) -> ft.Card:
        """Создание карточки для ввода истории"""
        final_badge = ft.Container(
            content=ft.Text("Терминальность", size=10, color="red"),
            bgcolor="red",
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=10
        ) if entry.get('is_final', False) else ft.Container()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Итерация {entry['iteration']}", 
                               weight=ft.FontWeight.BOLD, size=14),
                        final_badge
                    ]),
                    ft.Row([
                        ft.Text("Правило:", size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(f"'{entry['rule_pattern']}' → '{entry['rule_replacement']}'", 
                               size=12),
                    ]),
                    ft.Row([
                        ft.Text("Позиция:", size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(str(entry['position']), size=12),
                    ]),
                    ft.Row([
                        ft.Column([
                            ft.Text("До:", size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(entry['before'], size=12, selectable=True),
                        ], expand=1),
                        ft.Column([
                            ft.Text("После:", size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(entry['after'], size=12, selectable=True),
                        ], expand=1),
                    ]),
                ], tight=True),
                padding=10,
            )
        )
    
    def _clear_history(self, e):
        """Очистить отображаемую историю"""
        self.history_data.clear()
        self.history_list.controls.clear()
        self.history_list.controls.append(
            ft.Text("История очищена", style="bodyMedium")
        )
        self.stats_text.value = "Нет доступной статистики"
        self.history_list.update()
        self.stats_text.update()
    
    def build(self) -> ft.Column:
        """Построение компонента"""
        return ft.Column([
            ft.Row([
                ft.Text("История выполнения", size=20, weight=ft.FontWeight.BOLD),
                self.clear_button
            ]),
            self.stats_text,
            ft.Divider(),
            self.history_list
        ])