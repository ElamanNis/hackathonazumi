"""
Главное окно приложения с навигацией между страницами
"""

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
from pages.logo_page import LogoPage
from pages.login_page import LoginPage
from models.database import Database
from pages.dashboard_page import DashboardPage
from pages.container_management_page import ContainerManagementPage
from pages.artifacts_database_page import ArtifactsDatabasePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowTitle("Smart Container - Artifact Conservation System")

        # ПОЛНОЭКРАННЫЙ РЕЖИМ
        self.showMaximized()

        # Инициализация базы данных
        self.database = Database("artifacts.db")

        # Текущий пользователь (заполняется после логина)
        self.current_user = None

        # Создание QStackedWidget для переключения страниц
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Инициализация страниц
        self.init_pages()

        # Установка стиля окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }
        """)

    def init_pages(self):
        """Инициализация всех страниц приложения"""

        # Страница с логотипом (стартовая)
        self.logo_page = LogoPage(self)
        self.stacked_widget.addWidget(self.logo_page)  # index 0

        # Страница авторизации
        self.login_page = LoginPage(self)
        self.stacked_widget.addWidget(self.login_page)  # index 1

        self.dashboard_page = DashboardPage(self)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.container_management_page = ContainerManagementPage(self)
        self.stacked_widget.addWidget(self.container_management_page)
        # В методе setup_pages():
        self.artifacts_db_page = ArtifactsDatabasePage(self)
        self.stacked_widget.addWidget(self.artifacts_db_page)
        # index 2

        # Установить стартовую страницу
        self.stacked_widget.setCurrentIndex(0)

    def navigate_to(self, page_index):
        """
        Переключение на указанную страницу

        Args:
            page_index (int): Индекс страницы в QStackedWidget
        """
        self.stacked_widget.setCurrentIndex(page_index)

    def keyPressEvent(self, event):
        """Обработка нажатий клавиш (ESC для выхода из fullscreen)"""
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showMaximized()
        super().keyPressEvent(event)
