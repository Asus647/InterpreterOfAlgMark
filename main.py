#!/usr/bin/env python3
"""
Основная точка входа
"""

import sys
import os

# Добавление src в путь
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Основная точка вхождения"""
    try:
        from src.ui.main_window import main as app_main
        import flet as ft
        
        print("Запуск...")
        
        # Запуск приложения
        ft.app(target=app_main)
        
    except ImportError as e:
        print(f"Ошибка: Отсутствуют зависимости - {e}")
        print("Пожалуйста установите необходимые пакеты: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())