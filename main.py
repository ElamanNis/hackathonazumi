"""
Умный Контейнер для Консервации Артефактов
FLL SUBMERGED Season 2024-2025
Главный файл запуска приложения
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from main_window import MainWindow



def main():
    # Создание приложения
    app = QApplication(sys.argv)

    # Установка глобального шрифта
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Создание и показ главного окна
    window = MainWindow()
    window.show()

    # Запуск цикла обработки событий
    sys.exit(app.exec())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
