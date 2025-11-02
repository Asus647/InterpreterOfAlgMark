"""
Компонет редактора правил для графического пользовательского интерфейса
"""

import flet as ft
from typing import Callable, Optional, List
from ..core.markov_engine import Rule
from ..core.exceptions import RuleValidationError

class RuleEditor:
    """Компонет для редактирования правил"""
    
    def __init__(self, on_rule_change: Optional[Callable] = None, on_error: Optional[Callable] = None):
        self.on_rule_change = on_rule_change
        self.on_error = on_error
        self.rules: List[Rule] = []
        self.selected_rule_index = None
        
        # Создать компоненты пользовательского интерфейса
        self._create_components()
    
    def _create_components(self):
        """Создать компоненты пользовательского интерфейса"""
        # Поля ввода
        self.pattern_field = ft.TextField(
            label="Заменяемое (значение для поиска)",
            hint_text="Введите текст для поиска...",
            expand=True,
            on_change=self._validate_inputs
        )
        
        self.replacement_field = ft.TextField(
            label="Значение для замены",
            hint_text="Введет текст для замены...",
            expand=True,
            on_change=self._validate_inputs
        )
        
        self.final_checkbox = ft.Checkbox(
            label="Терминальность правила (остановка выполнения после применения)",
            value=False
        )
        
        # Отображение ошибок
        self.error_text = ft.Text(
            "",
            color=ft.colors.RED,
            size=12,
            visible=False
        )
        
        # Кнопки
        self.add_button = ft.ElevatedButton(
            "Добавить правило",
            icon=ft.icons.ADD,
            on_click=self._add_rule,
            disabled=True
        )
        
        self.update_button = ft.ElevatedButton(
            "Обновить правило",
            icon=ft.icons.UPDATE,
            on_click=self._update_rule,
            disabled=True
        )
        
        self.delete_button = ft.ElevatedButton(
            "Удалить правило",
            icon=ft.icons.DELETE,
            on_click=self._delete_rule,
            disabled=True
        )
        
        self.clear_button = ft.ElevatedButton(
            "Очистить все",
            icon=ft.icons.CLEAR_ALL,
            on_click=self._clear_rules
        )
        
        # Список правил
        self.rules_list = ft.ListView(expand=True)
        
        # Макет
        self.input_row = ft.Row([
            self.pattern_field,
            self.replacement_field,
            self.final_checkbox
        ])
        
        self.button_row = ft.Row([
            self.add_button,
            self.update_button,
            self.delete_button,
            self.clear_button
        ])
    
    def _validate_inputs(self, e=None):
        """Проверка полей ввода и изменение состояния кнопок"""
        pattern = self.pattern_field.value.strip() if self.pattern_field.value else ""
        
        # Стандартная проверка
        has_pattern = bool(pattern)
        
        # Обновление состояния конопки добавления
        self.add_button.disabled = not has_pattern
        self.add_button.update()
        
        # Очиста предыдущих ошибок если были исправлены
        if has_pattern:
            self._hide_error()
    
    def _show_error(self, message: str):
        """Показ сообщения об ошибке"""
        self.error_text.value = message
        self.error_text.visible = True
        self.error_text.update()
        
        # Отключение кнопки добавления правила если возникла ошибка
        self.add_button.disabled = True
        self.add_button.update()
    
    def _hide_error(self):
        """Спрятать сообщение об ошибке"""
        self.error_text.visible = False
        self.error_text.update()
    
    def _validate_rule_data(self, pattern: str, replacement: str, is_final: bool) -> bool:
        """
        Проверка данных правила перед его добавлением
        
        Returns:
            True если все хорошо, иначе False
        """
        try:
            # Попытка создать правило чтобы вызвать проверку
            Rule(pattern, replacement, is_final)
            return True
        except RuleValidationError as e:
            self._show_error(f"Проверка не пройдена: {str(e)}")
            return False
        except Exception as e:
            self._show_error(f"Неожиданная ошибка: {str(e)}")
            return False
    
    def _add_rule(self, e):
        """Добавление нового правила с соответствующей обработкой ошибок"""
        if not self.pattern_field.value:
            self._show_error("Заменяемое значение не может быть пустым")
            return
        
        pattern = self.pattern_field.value.strip()
        replacement = self.replacement_field.value or ""
        is_final = self.final_checkbox.value
        
        try:
            # Проверка данных правила
            if not self._validate_rule_data(pattern, replacement, is_final):
                return
            
            # Создание и добавление правила
            rule = Rule(pattern, replacement, is_final)
            self.rules.append(rule)
            self._refresh_rules_list()
            self._clear_inputs()
            self._hide_error()
            
            # Уведомление родительского компонента
            if self.on_rule_change:
                self.on_rule_change(self.rules)
                
        except RuleValidationError as e:
            self._show_error(f"Проверка правила не удалась: {str(e)}")
            if self.on_error:
                self.on_error(str(e))
        except Exception as e:
            error_msg = f"Не удалось добавить правило: {str(e)}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def _update_rule(self, e):
        """Изменить выбранное правило с соответствующей обработкой ошибок"""
        if self.selected_rule_index is None:
            self._show_error("Не выбрано правило для изменения")
            return
        
        pattern = self.pattern_field.value.strip() if self.pattern_field.value else ""
        replacement = self.replacement_field.value or ""
        is_final = self.final_checkbox.value
        
        if not pattern:
            self._show_error("Заменяемое значение не может быть пустым")
            return
        
        try:
            # Проверка данных правила
            if not self._validate_rule_data(pattern, replacement, is_final):
                return
            
            # Изменить правило
            self.rules[self.selected_rule_index] = Rule(pattern, replacement, is_final)
            self._refresh_rules_list()
            self._clear_selection()
            self._hide_error()
            
            # Уведомление родительского компонента
            if self.on_rule_change:
                self.on_rule_change(self.rules)
                
        except RuleValidationError as e:
            self._show_error(f"Проверка правила не удалась: {str(e)}")
            if self.on_error:
                self.on_error(str(e))
        except Exception as e:
            error_msg = f"Не удалось добавить правило: {str(e)}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def _delete_rule(self, e):
        """Удалить выбранное правило с соответствующей обработкой ошибок"""
        if self.selected_rule_index is None:
            self._show_error("Не выбрано правило для удаления")
            return
        
        try:
            # Сохранение данных правила для его потенциального удаления
            deleted_rule = self.rules[self.selected_rule_index]
            
            # Удаление правила
            self.rules.pop(self.selected_rule_index)
            self._refresh_rules_list()
            self._clear_selection()
            self._hide_error()
            
            # Уведомление родительского компонента
            if self.on_rule_change:
                self.on_rule_change(self.rules)
                
        except IndexError as e:
            error_msg = f"Индекс правила оказался за допустимыми границами: {self.selected_rule_index}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
        except Exception as e:
            error_msg = f"Не удалось удалить правило: {str(e)}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def _clear_rules(self, e):
        """Очистка всех правил с подтверждением и соответствующей обработкой ошибок"""
        if not self.rules:
            return
        
        try:
            # Очистить все правила
            self.rules.clear()
            self._refresh_rules_list()
            self._clear_selection()
            self._hide_error()
            
            # Уведомление родительского компонента
            if self.on_rule_change:
                self.on_rule_change(self.rules)
                
        except Exception as e:
            error_msg = f"Не удалось удалить правила: {str(e)}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def _clear_inputs(self):
        """Очистка полей ввода"""
        self.pattern_field.value = ""
        self.replacement_field.value = ""
        self.final_checkbox.value = False
        self.pattern_field.update()
        self.replacement_field.update()
        self.final_checkbox.update()
        self._validate_inputs()
    
    def _clear_selection(self):
        """Очистить выбор"""
        try:
            self.selected_rule_index = None
            self._clear_inputs()
            self._update_buttons_state()
            self._hide_error()
        except Exception as e:
            error_msg = f"Ошибка очистки выбора: {str(e)}"
            self._show_error(error_msg)
    
    def _update_buttons_state(self):
        """Обновление статусов кнопок в соответствии с вобором"""
        try:
            has_selection = self.selected_rule_index is not None
            self.update_button.disabled = not has_selection
            self.delete_button.disabled = not has_selection
            self.update_button.update()
            self.delete_button.update()
        except Exception as e:
            # Если обновление не удалось запомнить, но не показывать пользователю
            if self.on_error:
                self.on_error(f"Ошибка обновления кнопок: {str(e)}")
    
    def _refresh_rules_list(self):
        """Обновить отображаемый список правил"""
        try:
            self.rules_list.controls.clear()
            
            if not self.rules:
                # Показать пустое состояние
                empty_state = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.RULE, size=48, color=ft.colors.GREY_400),
                        ft.Text("Нет определенный правил", style="bodyMedium", color=ft.colors.GREY_600),
                        ft.Text("Добавить правила используя форму выше", style="bodySmall", color=ft.colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
                self.rules_list.controls.append(empty_state)
            else:
                for i, rule in enumerate(self.rules):
                    rule_card = self._create_rule_card(i, rule)
                    self.rules_list.controls.append(rule_card)
            
            self.rules_list.update()
            
        except Exception as e:
            error_msg = f"Ошибка обновления списка правил: {str(e)}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def _create_rule_card(self, index: int, rule: Rule) -> ft.Card:
        """Создание карточки для отображения правил"""
        try:
            final_badge = ft.Container(
                content=ft.Text("Терминальность", size=10, color=ft.colors.RED),
                bgcolor=ft.colors.RED_100,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=10
            ) if rule.is_final else ft.Container()
            
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Правило {index + 1}", weight=ft.FontWeight.BOLD),
                            final_badge
                        ]),
                        ft.Row([
                            ft.Text(f"Найти: '{rule.pattern}'", size=14),
                            ft.Icon(ft.icons.ARROW_FORWARD, size=16),
                            ft.Text(f"Заменить: '{rule.replacement}'", size=14),
                        ])
                    ]),
                    padding=10,
                    on_click=lambda e, idx=index: self._select_rule(idx)
                )
            )
        except Exception as e:
            # Резервная карта на случай ошибки
            return ft.Card(
                content=ft.Container(
                    content=ft.Text(f"Ошибка отобрежения карты {index + 1}", color=ft.colors.RED),
                    padding=10
                )
            )
    
    def _select_rule(self, index: int):
        """Выбрать правило для изменения"""
        try:
            if index < 0 or index >= len(self.rules):
                self._show_error(f"Неверный индекс правила: {index}")
                return
            
            self.selected_rule_index = index
            rule = self.rules[index]
            
            self.pattern_field.value = rule.pattern
            self.replacement_field.value = rule.replacement
            self.final_checkbox.value = rule.is_final
            
            self.pattern_field.update()
            self.replacement_field.update()
            self.final_checkbox.update()
            self._update_buttons_state()
            self._hide_error()
            
        except IndexError as e:
            self._show_error(f"Правило с данным индексом не найдено {index}")
        except Exception as e:
            error_msg = f"Ошибка выбора правила: {str(e)}"
            self._show_error(error_msg)
    
    def get_rules(self) -> List[Rule]:
        """Получить текущие правила"""
        try:
            return self.rules.copy()
        except Exception as e:
            if self.on_error:
                self.on_error(f"Ошибка получения правил: {str(e)}")
            return []
    
    def set_rules(self, rules: List[Rule]):
        """Установить правила"""
        try:
            self.rules = rules.copy() if rules else []
            self._refresh_rules_list()
            self._clear_selection()
            self._hide_error()
            
            # Уведомление родительского компонента
            if self.on_rule_change:
                self.on_rule_change(self.rules)
                
        except Exception as e:
            error_msg = f"Ошибка установки правил: {str(e)}"
            self._show_error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
    
    def build(self) -> ft.Column:
        """Посстроение компонента"""
        return ft.Column([
            ft.Text("Редактор правил", size=20, weight=ft.FontWeight.BOLD),
            self.input_row,
            self.error_text,
            self.button_row,
            ft.Divider(),
            ft.Text("Текущие правила", size=16, weight=ft.FontWeight.BOLD),
            self.rules_list
        ])