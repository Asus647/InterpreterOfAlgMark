"""
Основное окно
"""

import flet as ft
from typing import List, Optional
from ..core.markov_engine import MarkovEngine, Rule
from ..core.exceptions import RuleValidationError, ExecutionLimitError
from ..utils.presets import RulePresets
from ..utils.file_io import ProjectManager
from .rule_editor import RuleEditor
from .history_viewer import HistoryViewer

class MarkovApp:
    """Класс исполняющий алгоритмы"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.engine = MarkovEngine()
        self.project_manager = ProjectManager()
        self.rule_editor = RuleEditor(
            on_rule_change=self._on_rules_changed,
            on_error=self._show_error_dialog
        )
        self.history_viewer = HistoryViewer()
        
        # Сначала создаем кнопки меню
        self._create_menu_buttons()
        
        # Затем создаем остальные компоненты
        self._create_components()
    
    def _create_menu_buttons(self):
        """Создание кнопок для взаимодействия с файлами"""
        self.save_button = ft.ElevatedButton(
            "Сохранить проект",
            icon="save",
            on_click=self._save_project,
        )
        
        self.load_button = ft.ElevatedButton(
            "Загрузить проект", 
            icon="folder_open",
            on_click=self._load_project
        )
        
        self.export_button = ft.ElevatedButton(
            "Экспорт правил",
            icon="exit_to_app",
            on_click=self._export_rules
        )
        
        self.import_button = ft.ElevatedButton(
            "Импорт правил",
            icon="input", 
            on_click=self._import_rules
        )
    
    def _create_components(self):
        """Создание основных элементов ПИ"""
        # Текстовые поля для ввода/вывода
        self.input_text = ft.TextField(
            label="Входной текст",
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
            hint_text="Введите текст для обработки..."
        )
        
        self.output_text = ft.TextField(
            label="Выходной текст",
            multiline=True,
            min_lines=5,
            max_lines=10,
            expand=True,
            read_only=True
        )
        
        # Исполняющие кнопки
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
        
        # Выпадающий список пресетов
        self.presets_dropdown = ft.Dropdown(
            label="Загрузить пресет",
            hint_text="Выберите готовый набор правил",
            options=[
                ft.dropdown.Option('transliteration', 'Транслитерация (кириллица в латиницу)'),
                ft.dropdown.Option('text_normalization', 'Нормализация текста'),
                ft.dropdown.Option('html_escaping', 'HTML-экранирование'),
                ft.dropdown.Option('markdown_cleanup', 'Очистка Markdown'),
            ],
            on_change=self._load_preset,
            expand=True
        )
        
        # Отображение статуса
        self.status_bar = ft.Text("Готов", style="bodySmall")
        
        # Индикатор прогресса
        self.progress_ring = ft.ProgressRing(visible=False)
        
        # Создание окон
        self._create_tabs()
    
    def _create_tabs(self):
        """Создание основных окон"""
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
        """Построение окна редактора"""
        text_area_row = ft.Row([
            ft.Column([self.input_text], expand=1),
            ft.Column([self.output_text], expand=1),
        ])
        
        file_ops_row = ft.Row([
            self.save_button,
            self.load_button,
            self.export_button,
            self.import_button,
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
                ft.Text("Файловые операции", size=16, weight=ft.FontWeight.BOLD),
                file_ops_row,
                ft.Divider(),
                text_area_row,
                control_row,
                status_row,
                ft.Divider(),
                self.rule_editor.build()
            ]),
            padding=20
        )
    
    def _build_history_tab(self) -> ft.Container:
        """Построение окна с историей выполнения правил"""
        return ft.Container(
            content=self.history_viewer.build(),
            padding=20
        )
    
    def _on_rules_changed(self, rules: List[Rule]):
        """Вызов когда правила изменились"""
        try:
            self.engine.clear_rules()
            for rule in rules:
                self.engine.add_rule(rule.pattern, rule.replacement, rule.is_final)
            
            self._update_status(f"Правила обновлены: {len(rules)} правил загружено")
            
        except RuleValidationError as e:
            self._show_error_dialog(f"Ошибка валидации правил: {str(e)}")
        except Exception as e:
            self._show_error_dialog(f"Ошибка обновления правил: {str(e)}")
    
    def _load_preset(self, e):
        """Загрузить выбранный пресет"""
        preset_key = self.presets_dropdown.value
        if not preset_key:
            return
        
        try:
            presets = RulePresets.get_presets()
            if preset_key in presets:
                # Преобразование кортежей в объекты правил
                rules = []
                for pattern, replacement, is_final in presets[preset_key]:
                    rules.append(Rule(pattern, replacement, is_final))
                
                self.rule_editor.set_rules(rules)
                self._update_status(f"Загружен пресет: {preset_key}")
                
                # Отображение информации о загруженном пресете
                rule_count = len(rules)
                final_rules = sum(1 for r in rules if r.is_final)
                self._show_info_dialog(
                    "Пресет загружен",
                    f"Успешно загружен пресет '{preset_key.replace('_', ' ').title()}'.\n\n"
                    f"• Правил загружено: {rule_count}\n"
                    f"• Финальных правил: {final_rules}\n"
                    f"• Обычных правил: {rule_count - final_rules}"
                )
            else:
                self._show_error_dialog(f"Пресет '{preset_key}' не найден")
                
        except Exception as e:
            self._show_error_dialog(f"Ошибка загрузки пресета: {str(e)}")
    
    async def _execute_algorithm(self, e):
        """Выполнить алгоритм"""
        input_text = self.input_text.value.strip()
        if not input_text:
            self._show_warning_dialog("Пустой ввод", "Пожалуйста, введите текст для обработки.")
            return
        
        if not self.engine.rules:
            self._show_warning_dialog("Нет правил", "Пожалуйста, определите хотя бы одно правило перед выполнением.")
            return
        
        # Показать прогресс
        self._set_processing(True)
        
        try:
            # Выполнить алгоритм
            result = self.engine.execute(input_text)
            
            # Обновить результат
            self.output_text.value = result['output']
            self.output_text.update()
            
            # Обновить историю применения правил
            self.history_viewer.set_history(
                result['history'], 
                result['statistics']
            )
            
            # Обновить статус
            status_msg = (f"Завершено: {result['statistics']['iterations']} итераций, "
                         f"{result['statistics']['total_replacements']} замен")
            self._update_status(status_msg)
            
            # Показать преупреждения если есть
            if result['warnings']:
                self._show_warnings(result['warnings'])
                
        except ExecutionLimitError as e:
            self._show_error_dialog(
                "Достигнут лимит выполнения",
                f"Алгоритм был остановлен для предотвращения бесконечного выполнения.\n\n"
                f"Причина: {str(e)}\n\n"
                f"Это может указывать на:\n"
                f"• Потенциальный бесконечный цикл в правилах\n"
                f"• Правила, вызывающие неограниченный рост\n"
                f"• Сложные взаимодействия правил\n\n"
                f"Проверьте правила на наличие циклов или взаимных замен."
            )
            self._update_status(f"Остановлено: {str(e)}")
            
        except Exception as ex:
            error_msg = str(ex)
            self._show_error_dialog(f"Ошибка выполнения: {error_msg}")
            self._update_status(f"Ошибка: {error_msg}")
        
        finally:
            self._set_processing(False)
    
    def _clear_all(self, e):
        """Очищает все поля"""
        try:
            self.input_text.value = ""
            self.output_text.value = ""
            self.input_text.update()
            self.output_text.update()
            self._update_status("Все поля очищены")
        except Exception as e:
            self._show_error_dialog(f"Ошибка очистки полей: {str(e)}")
    
    def _set_processing(self, processing: bool):
        """Задает состояние обработки"""
        try:
            self.execute_button.disabled = processing
            self.progress_ring.visible = processing
            self.execute_button.update()
            self.progress_ring.update()
        except Exception as e:
            pass
    
    def _update_status(self, message: str):
        """Обновление статуса"""
        try:
            self.status_bar.value = message
            self.status_bar.update()
        except Exception as e:
            pass
    
    # Операции с файлами
    async def _save_project(self, e):
        """Сохранить текущий проект в файл"""
        try:
            rules = self.rule_editor.get_rules()
            input_text = self.input_text.value or ""
            output_text = self.output_text.value or ""
            
            # Просто сохраняем в текущую директорию
            filepath = "project.json"
            success = self.project_manager.save_project(
                filepath, rules, input_text, output_text
            )
            
            if success:
                self._show_info_dialog("Успех", f"Проект успешно сохранен в {filepath}!")
                self._update_status(f"Проект сохранен: {filepath}")
            else:
                self._show_error_dialog("Ошибка", "Не удалось сохранить проект")
                
        except Exception as ex:
            self._show_error_dialog("Ошибка сохранения", str(ex))
    
    async def _load_project(self, e):
        """Загрузить проект из файла"""
        try:
            # Просто загружаем из текущей директории
            filepath = "project.json"
            project_data = self.project_manager.load_project(filepath)
            
            if project_data:
                self.rule_editor.set_rules(project_data['rules'])
                self.input_text.value = project_data.get('input_text', '')
                self.output_text.value = project_data.get('output_text', '')
                self.input_text.update()
                self.output_text.update()
                self._update_status(f"Проект загружен: {filepath}")
                self._show_info_dialog("Успех", "Проект успешно загружен!")
            else:
                self._show_error_dialog("Ошибка", f"Не удалось загрузить проект из {filepath}")
                
        except Exception as ex:
            self._show_error_dialog("Ошибка загрузки", str(ex))
    
    async def _export_rules(self, e):
        """Экспорт правил в json файл"""
        try:
            rules = self.rule_editor.get_rules()
            
            # Просто сохраняем в текущую директорию
            filepath = "rules_export.json"
            success = self.project_manager.export_rules_json(filepath, rules)
            
            if success:
                self._show_info_dialog("Успех", f"Правила экспортированы в {filepath}: {len(rules)} правил")
                self._update_status(f"Правила экспортированы: {filepath}")
            else:
                self._show_error_dialog("Ошибка", "Не удалось экспортировать правила")
                
        except Exception as ex:
            self._show_error_dialog("Ошибка экспорта", str(ex))
    
    async def _import_rules(self, e):
        """Импорт правил из json файла"""
        try:
            # Просто загружаем из текущей директории
            filepath = "rules_export.json"
            rules = self.project_manager.import_rules_json(filepath)
            
            if rules:
                self.rule_editor.set_rules(rules)
                self._update_status(f"Правила импортированы: {len(rules)} правил")
                self._show_info_dialog("Успех", f"Правила импортированы: {len(rules)} правил")
            else:
                self._show_error_dialog("Ошибка", f"Не удалось импортировать правила из {filepath}")
                
        except Exception as ex:
            self._show_error_dialog("Ошибка импорта", str(ex))
    
    def _show_warnings(self, warnings: List[str]):
        """Показать окно с предупреждениями"""
        if not warnings:
            return
        
        warning_content = "\n• ".join(warnings)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Обнаружены потенциальные проблемы"),
            content=ft.Column([
                ft.Text("Обнаружены следующие потенциальные проблемы:"),
                ft.Container(
                    content=ft.Text(f"• {warning_content}"),
                    margin=ft.margin.only(top=10, left=10),
                    padding=ft.padding.all(10),
                    bgcolor="yellow",
                    border_radius=8
                ),
                ft.Text("\nВы можете продолжить выполнение, но будьте осторожны с возможными бесконечными циклами."),
            ], tight=True),
            actions=[
                ft.TextButton("Продолжить", on_click=lambda e: self._close_dialog(dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_warning_dialog(self, title: str, message: str):
        """Показать окно с предупреждениями"""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog)),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_error_dialog(self, title: str = "Ошибка", message: str = ""):
        """Показать окно с ошибками"""
        # Если передана только message (для обратной совместимости)
        if message == "" and title != "Ошибка":
            message = title
            title = "Ошибка"
        
        # Обрезать очень длинные ошибки
        if len(message) > 500:
            message = message[:500] + "...\n\n(Сообщение об ошибке усечено)"
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color="red"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog)),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _show_info_dialog(self, title: str, message: str):
        """Показать окно с информацией"""
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog(dialog)),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog: ft.AlertDialog):
        """Закрыть окно"""
        dialog.open = False
        self.page.update()
    
    def build(self) -> ft.Tabs:
        """Построение основного окна"""
        return self.main_tabs

def main(page: ft.Page):
    """Входная точка программы"""
    # Конфигурация страницы
    page.title = "Интерпретатор Алгоритмов Маркова"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE
    
    # Задать размер окна
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 800
    page.window.min_height = 600
    
    # Создать и добавить приложение
    app = MarkovApp(page)
    page.add(app.build())

if __name__ == "__main__":
    ft.app(target=main, view = ft.WEB_BROWSER)