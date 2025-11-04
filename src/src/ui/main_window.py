"""
Основное окно приложения
"""

import flet as ft
from typing import List, Optional
from ..core.markov_engine import MarkovEngine, Rule
from ..core.exceptions import RuleValidationError, ExecutionLimitError
from ..utils.presets import RulePresets
from .rule_editor import RuleEditor
from .history_viewer import HistoryViewer

class MarkovApp:
    """Основной класс приложения"""
    
    def __init__(self, page: Optional[ft.Page] = None):
        self.page = page
        self.engine = MarkovEngine()
        self.rule_editor = RuleEditor(
            on_rule_change=self._on_rules_changed,
            on_error=self._show_error_dialog
        )
        self.history_viewer = HistoryViewer()
        
        # Создание компонентов ПИ
        self._create_components()
    
    def _create_components(self):
        """Создание основных компонентов ПИ"""
        # Текстовые поля для ввода\вывода
        self.input_text = ft.TextField(
            label="Вводимый текст",
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
            hint_text="Введите текст для начала работы..."
        )
        
        self.output_text = ft.TextField(
            label="Результат",
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
            read_only=True
        )
        
        # Кнопки
        self.execute_button = ft.ElevatedButton(
            "Выполнить алгоритм",
            icon="play_arrow",
            on_click=self._execute_algorithm,
            expand=True
        )
        
        self.clear_button = ft.ElevatedButton(
            "Очистить все",
            icon="clear_all",
            on_click=self._clear_all,
            expand=True
        )
        
        # Шаблонные алгоритмы
        self.presets_dropdown = ft.Dropdown(
            label="Загрузить шаблон",
            hint_text="Выберите предопределенный набор правил",
            options=[
                ft.dropdown.Option(key, key.replace('_', ' ').title())
                for key in RulePresets.get_presets().keys()
            ],
            on_change=self._load_preset,
            expand=True
        )
        
        # Отображение статуса
        self.status_bar = ft.Text("Ready", style="bodySmall")
        
        # Индикатор прогресса
        self.progress_ring = ft.ProgressRing(visible=False)
        
        # Окна для просмотра различного контента
        self._create_tabs()
    
    def _create_tabs(self):
        """Основное окно"""
        self.main_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Редактор",
                    icon="edit",
                    content=self._build_editor_tab()
                ),
                ft.Tab(
                    text="История",
                    icon="history",
                    content=self._build_history_tab()
                ),
            ]
        )
    
    def _build_editor_tab(self) -> ft.Container:
        """Окно редактора"""
        text_area_row = ft.Row([
            ft.Column([self.input_text], expand=1),
            ft.Column([self.output_text], expand=1),
        ])
        
        control_row = ft.Row([
            self.execute_button,
            self.clear_button,
            self.presets_dropdown,
        ])
        
        status_row = ft.Row([
            self.status_bar,
            self.progress_ring
        ])
        
        return ft.Container(
            content=ft.Column([
                text_area_row,
                control_row,
                status_row,
                ft.Divider(),
                self.rule_editor.build()
            ]),
            padding=20
        )
    
    def _build_history_tab(self) -> ft.Container:
        """Окно просмотра истории"""
        return ft.Container(
            content=self.history_viewer.build(),
            padding=20
        )
    
    def _on_rules_changed(self, rules: List[Rule]):
        """Вызов когда правила были изменены"""
        try:
            self.engine.clear_rules()
            for rule in rules:
                self.engine.add_rule(rule.pattern, rule.replacement, rule.is_final)
            
            self._update_status(f"Измененные правила: {len(rules)} правила загружены")
            
        except RuleValidationError as e:
            self._show_error_dialog(f"Ошибка проверки првила: {str(e)}")
        except Exception as e:
            self._show_error_dialog(f"Ошибка изменения правила: {str(e)}")
    
    def _load_preset(self, e):
        """Загрузить выбранные шаблоны"""
        preset_key = self.presets_dropdown.value
        if not preset_key:
            return
        
        try:
            presets = RulePresets.get_presets()
            if preset_key in presets:
                # Преобразование набора кортежей в объект набора правил
                rules = []
                for pattern, replacement, is_final in presets[preset_key]:
                    rules.append(Rule(pattern, replacement, is_final))
                
                self.rule_editor.set_rules(rules)
                self._update_status(f"Загруженные шаблоны: {preset_key}")
                
                # Показать информацию об загруженных шаблонах
                rule_count = len(rules)
                final_rules = sum(1 for r in rules if r.is_final)
                self._show_info_dialog(
                    "Шаблон загружен",
                    f"Успешно загружен '{preset_key.replace('_', ' ').title()}' шаблон.\n\n"
                    f"• Загружено правил: {rule_count}\n"
                    f"• Терминальных правил: {final_rules}\n"
                    f"• Обычные правила: {rule_count - final_rules}"
                )
            else:
                self._show_error_dialog(f"Шаблон '{preset_key}' не найден")
                
        except Exception as e:
            self._show_error_dialog(f"Ошибка загрузки шаблона: {str(e)}")
    
    async def _execute_algorithm(self, e):
        """Выполнение алгоритма"""
        input_text = self.input_text.value.strip()
        if not input_text:
            self._show_warning_dialog("Поле вводу пусто", "Введите текст для выполнения.")
            return
        
        if not self.engine.rules:
            self._show_warning_dialog("Нет правил", "Определите хотя бы 1 правиле перед выполнением алгоритма.")
            return
        
        # Отображение прогресса
        self._set_processing(True)
        
        try:
            # Выполнить алгоритм
            result = self.engine.execute(input_text)
            
            # Обновить результат
            self.output_text.value = result['output']
            self.output_text.update()
            
            # Обновить историю
            self.history_viewer.set_history(
                result['history'], 
                result['statistics']
            )
            
            # Стутас обновления
            status_msg = (f"Сделано: {result['statistics']['iterations']} итераций, "
                         f"{result['statistics']['total_replacements']} замен")
            self._update_status(status_msg)
            
            # Показать предупреждения есть есть
            if result['warnings']:
                self._show_warnings(result['warnings'])
                
        except ExecutionLimitError as e:
            self._show_warning_dialog(
                "Превышено ограничение на выполнение",
                f"Алгоритм был остановлен чтобы не допустить бесконечное выполнение.\n\n"
                f"Причина: {str(e)}\n\n"
                f"Это может показать:\n"
                f"• Потенциальное зацикливание в правилах\n"
                f"• Правила могут вызывать неограниченный рост текста\n"
                f"• Сложные итерации правил\n\n"
                f"Проверьте свои правила на зацикливание и взаимозаменение."
            )
            self._update_status(f"Остановлено: {str(e)}")
            
        except Exception as ex:
            error_msg = str(ex)
            self._show_error_dialog(f"Ошибка выполнения: {error_msg}")
            self._update_status(f"Ошибка: {error_msg}")
        
        finally:
            self._set_processing(False)
    
    def _clear_all(self, e):
        """Очистить все поля ввода\вывода"""
        try:
            self.input_text.value = ""
            self.output_text.value = ""
            self.input_text.update()
            self.output_text.update()
            self._update_status("Все поля очищены")
        except Exception as e:
            self._show_error_dialog(f"Ошибка очистки полей: {str(e)}")
    
    def _set_processing(self, processing: bool):
        """Задать статус обработки"""
        self.execute_button.disabled = processing
        self.progress_ring.visible = processing
        self.execute_button.update()
        self.progress_ring.update()
    
    def _update_status(self, message: str):
        """Обновить статус шкалы"""
        self.status_bar.value = message
        self.status_bar.update()
    
    def _show_warnings(self, warnings: List[str]):
        """Показать предупреждений"""
        if not warnings or not self.page:
            return
        
        warning_content = "\n• ".join(warnings)
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        def continue_execution(e):
            self.page.dialog.open = False
            self.page.update()
        
        warning_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Обнаружены потенциальные проблема"),
            content=ft.Column([
                ft.Text("Следующие потенциальные проблемы были обнаружены:"),
                ft.Container(
                    content=ft.Text(f"• {warning_content}"),
                    margin=ft.margin.only(top=10, left=10),
                    padding=ft.padding.all(10),
                    bgcolor="yellow",
                    border_radius=8
                ),
                ft.Text("\nВы можете продолжить выполнение, но будьте осторожны."),
            ], tight=True),
            actions=[
                ft.TextButton("Все равно продолжить", on_click=continue_execution),
                ft.TextButton("просмотреть ошибки", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = warning_dialog
        warning_dialog.open = True
        self.page.update()
    
    def _show_warning_dialog(self, title: str, message: str):
        """Показать окно предупреждений"""
        if not self.page:
            print(f"Предупреждение: {title} - {message}")
            return
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        warning_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
        )
        
        self.page.dialog = warning_dialog
        warning_dialog.open = True
        self.page.update()
    
    def _show_error_dialog(self, error_message: str):
        """Показать окно ошибок"""
        if not self.page:
            print(f"Ошибка: {error_message}")
            return
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        # Обрезать очень длинные сообщение об ошибках
        if len(error_message) > 500:
            error_message = error_message[:500] + "...\n\n(Сообщение об ошибке обрезано)"
        
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ошибка", color="red"),
            content=ft.Text(error_message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
        )
        
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()
    
    def _show_info_dialog(self, title: str, message: str):
        """Покащать окно с информацией"""
        if not self.page:
            print(f"Информация: {title} - {message}")
            return
        
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        info_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
        )
        
        self.page.dialog = info_dialog
        info_dialog.open = True
        self.page.update()
    
    def build(self) -> ft.Tabs:
        """Запуск основного окна"""
        return self.main_tabs

def main(page: ft.Page):
    """Входная точка"""
    # Конфигурация страницы
    page.title = "Интерпретатор Алгоритмов Маркова"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    # Размер страницы
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 800
    page.window.min_height = 600
    
    # Создать и добавить
    app = MarkovApp(page)
    page.add(app.build())

if __name__ == "__main__":
    ft.app(target=main)