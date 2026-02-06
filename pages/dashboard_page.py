"""
Главная панель управления (Dashboard)
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGridLayout, QFrame, QScrollArea,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PySide6.QtGui import QFont, QPainter, QPixmap, QLinearGradient, QColor
from datetime import datetime

class DashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Фон с лёгким оверлеем
        overlay = QWidget()
        overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 23, 42, 0.8);
            }
        """)

        overlay_layout = QVBoxLayout()
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)

        # ============= ВЕРХНЯЯ ПАНЕЛЬ (Header) =============
        header = self.create_header()
        overlay_layout.addWidget(header)

        # ============= СКРОЛЛИРУЕМАЯ ОБЛАСТЬ КОНТЕНТА =============
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(51, 65, 85, 0.3);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(245, 158, 11, 0.6);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(245, 158, 11, 0.8);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Контент внутри скролла
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(50, 40, 50, 40)
        content_layout.setSpacing(35)

        # ============= КАРТОЧКИ СТАТИСТИКИ =============
        stats_container = self.create_statistics_cards()
        content_layout.addWidget(stats_container)

        # ============= ГЛАВНЫЕ КНОПКИ НАВИГАЦИИ =============
        main_buttons = self.create_main_buttons()
        content_layout.addWidget(main_buttons)

        # ============= ПОСЛЕДНИЕ АКТИВНОСТИ =============
        recent_activity = self.create_recent_activity()
        content_layout.addWidget(recent_activity)

        content_layout.addStretch()

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        overlay_layout.addWidget(scroll_area)

        overlay.setLayout(overlay_layout)
        main_layout.addWidget(overlay)

        self.setLayout(main_layout)

        # Загрузка фона
        self.background_pixmap = None
        self.load_background("img.png")

        # Обновление времени каждую секунду
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

    def create_header(self):
        """Создание верхней панели"""
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 41, 59, 0.5);
                border: none;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(50, 0, 50, 0)

        # Левая часть - приветствие
        left_section = QWidget()
        left_section.setStyleSheet("background: transparent; border: none;")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # Получаем имя пользователя
        user = self.main_window.current_user
        username = user['username'] if user else "User"
        full_name = user.get('full_name', username) if user else username

        greeting_label = QLabel(f"Welcome back, {full_name}")
        greeting_font = QFont("Segoe UI", 24, QFont.Bold)
        greeting_label.setFont(greeting_font)
        greeting_label.setStyleSheet("""
            QLabel {
                color: #f1f5f9;
                background: transparent;
                border: none;
            }
        """)

        self.subtitle_label = QLabel("Ready to preserve history")
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)

        left_layout.addWidget(greeting_label)
        left_layout.addWidget(self.subtitle_label)
        left_section.setLayout(left_layout)

        # Правая часть - дата, время, статус
        right_section = QWidget()
        right_section.setStyleSheet("background: transparent; border: none;")
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)

        # Текущее время
        self.time_label = QLabel()
        self.update_time()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
                background-color: rgba(51, 65, 85, 0.4);
                padding: 12px 18px;
                border-radius: 12px;
                border: none;
            }
        """)

        # Кнопка выхода
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedSize(90, 42)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.3);
                color: #fecaca;
            }
            QPushButton:pressed {
                background-color: rgba(239, 68, 68, 0.4);
            }
        """)

        right_layout.addWidget(self.time_label)
        right_layout.addWidget(logout_btn)
        right_section.setLayout(right_layout)

        layout.addWidget(left_section)
        layout.addStretch()
        layout.addWidget(right_section)

        header.setLayout(layout)
        return header

    def create_statistics_cards(self):
        """Создание карточек статистики"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        grid = QGridLayout()
        grid.setSpacing(20)

        # Данные статистики
        stats = [
            {
                "title": "Total Artifacts",
                "value": "16",
                "icon": "📦",
                "color": "#60a5fa",
                "bg": "rgba(96, 165, 250, 0.12)",
                "change": "+12 this week"
            },
            {
                "title": "Active Containers",
                "value": "1",
                "icon": "🔧",
                "color": "#34d399",
                "bg": "rgba(52, 211, 153, 0.12)",
                "change": "2 in use now"
            },
            {
                "title": "Classiffication Accuracy",
                "value": "92.2%",
                "icon": "📸",
                "color": "#fbbf24",
                "bg": "rgba(251, 191, 36, 0.12)",
                "change": "Last: 2 hours ago"
            },
            {
                "title": "Database Size",
                "value": "1.2 GB",
                "icon": "💾",
                "color": "#a78bfa",
                "bg": "rgba(167, 139, 250, 0.12)",
                "change": "453 photos stored"
            }
        ]

        for i, stat in enumerate(stats):
            card = self.create_stat_card(
                stat["title"],
                stat["value"],
                stat["icon"],
                stat["color"],
                stat["bg"],
                stat["change"]
            )
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)

        container.setLayout(grid)
        return container

    def create_stat_card(self, title, value, icon, color, bg_color, change):
        """Создание одной карточки статистики"""
        card = QWidget()
        card.setFixedHeight(160)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(51, 65, 85, 0.35);
                border-radius: 16px;
                border: none;
            }}
            QWidget:hover {{
                background-color: rgba(51, 65, 85, 0.5);
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        # Верхняя часть - заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(title_label)

        # Средняя часть - иконка и значение
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(15)

        # Иконка в цветном кружке
        icon_container = QWidget()
        icon_container.setFixedSize(56, 56)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 28px;
                border: none;
            }}
        """)

        icon_layout = QVBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                background: transparent;
                border: none;
            }
        """)

        icon_layout.addWidget(icon_label)
        icon_container.setLayout(icon_layout)

        # Значение
        value_label = QLabel(value)
        value_font = QFont("Segoe UI", 38, QFont.Bold)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background: transparent;
                border: none;
            }}
        """)

        middle_layout.addWidget(icon_container)
        middle_layout.addWidget(value_label)
        middle_layout.addStretch()

        layout.addLayout(middle_layout)
        layout.addStretch()

        # Нижняя часть - изменение
        change_label = QLabel(change)
        change_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(change_label)

        card.setLayout(layout)
        return card

    def create_main_buttons(self):
        """Создание основных кнопок навигации"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Заголовок секции
        title = QLabel("Quick Actions")
        title_font = QFont("Segoe UI", 22, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #f1f5f9;
                background: transparent;
                padding: 5px 0 10px 0;
                border: none;
            }
        """)
        layout.addWidget(title)

        # Grid с кнопками
        grid = QGridLayout()
        grid.setSpacing(20)

        buttons_data = [
            {
                "text": "Container Management",
                "icon": "🔧",
                "color": "#34d399",
                "bg": "rgba(52, 211, 153, 0.15)",
                "description": "Control and monitor active containers"
            },
            {
                "text": "Artifact Database",
                "icon": "📚",
                "color": "#60a5fa",
                "bg": "rgba(96, 165, 250, 0.15)",
                "description": "Browse and search discoveries"
            },
            {
                "text": "Discovery Map",
                "icon": "🗺️",
                "color": "#fbbf24",
                "bg": "rgba(251, 191, 36, 0.15)",
                "description": "View excavation site locations"
            },
            {
                "text": "Settings",
                "icon": "⚙️",
                "color": "#a78bfa",
                "bg": "rgba(167, 139, 250, 0.15)",
                "description": "Configure system preferences"
            }
        ]

        for i, btn_data in enumerate(buttons_data):
            btn = self.create_action_button(
                btn_data["text"],
                btn_data["icon"],
                btn_data["color"],
                btn_data["bg"],
                btn_data["description"]
            )
            row = i // 2
            col = i % 2
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)
        container.setLayout(layout)
        return container

    def create_action_button(self, text, icon, color, bg_color, description):
        """Создание большой кнопки действия"""
        button = QPushButton()
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(150)

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(51, 65, 85, 0.35);
                border: none;
                border-radius: 16px;
                text-align: left;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(51, 65, 85, 0.55);
            }}
            QPushButton:pressed {{
                background-color: rgba(51, 65, 85, 0.65);
            }}
        """)

        # Layout внутри кнопки
        layout = QHBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Иконка в цветном кружке
        icon_container = QWidget()
        icon_container.setFixedSize(70, 70)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 35px;
                border: none;
            }}
        """)

        icon_layout = QVBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                background: transparent;
                border: none;
            }
        """)

        icon_layout.addWidget(icon_label)
        icon_container.setLayout(icon_layout)

        # Текст и описание
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent; border: none;")
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)
        text_layout.setContentsMargins(0, 10, 0, 0)

        text_label = QLabel(text)
        text_font = QFont("Segoe UI", 19, QFont.Bold)
        text_label.setFont(text_font)
        text_label.setStyleSheet("""
            QLabel {
                color: #f1f5f9;
                background: transparent;
                border: none;
            }
        """)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 13px;
                background: transparent;
                border: none;
            }
        """)

        text_layout.addWidget(text_label)
        text_layout.addWidget(desc_label)
        text_layout.addStretch()
        text_container.setLayout(text_layout)

        layout.addWidget(icon_container)
        layout.addWidget(text_container, 1)

        button.setLayout(layout)

        # Обработчики
        if "Container" in text:
            button.clicked.connect(lambda: self.main_window.navigate_to(3))
        elif "Database" in text:
            button.clicked.connect(lambda: self.main_window.navigate_to(4))
        elif "Map" in text:
            button.clicked.connect(lambda: print("Opening Map..."))
        elif "Settings" in text:
            button.clicked.connect(lambda: print("Opening Settings..."))

        return button

    def create_recent_activity(self):
        """Создание секции последних активностей"""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Recent Activity")
        title_font = QFont("Segoe UI", 22, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #f1f5f9;
                background: transparent;
                padding: 5px 0 10px 0;
                border: none;
            }
        """)
        layout.addWidget(title)

        # Панель активности
        activity_panel = QWidget()
        activity_panel.setStyleSheet("""
            QWidget {
                background-color: rgba(51, 65, 85, 0.35);
                border-radius: 16px;
                border: none;
            }
        """)

        activity_layout = QVBoxLayout()
        activity_layout.setContentsMargins(28, 24, 28, 24)
        activity_layout.setSpacing(18)

        # Примеры активности
        activities = [
            {"time": "2 hours ago", "action": "Scanned bronze artifact from site A-12", "color": "#34d399"},
            {"time": "5 hours ago", "action": "Updated container #2 climate settings", "color": "#60a5fa"},
            {"time": "Yesterday", "action": "Added 3 ceramic pieces to database", "color": "#fbbf24"},
        ]

        for activity in activities:
            item = self.create_activity_item(activity["time"], activity["action"], activity["color"])
            activity_layout.addWidget(item)

        activity_panel.setLayout(activity_layout)
        layout.addWidget(activity_panel)

        container.setLayout(layout)
        return container

    def create_activity_item(self, time, action, color):
        """Создание элемента активности"""
        item = QWidget()
        item.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        # Индикатор
        indicator = QLabel("●")
        indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                background: transparent;
                border: none;
            }}
        """)
        indicator.setFixedWidth(20)

        # Информация
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        action_label = QLabel(action)
        action_label.setStyleSheet("""
            QLabel {
                color: #e2e8f0;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)

        time_label = QLabel(time)
        time_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)

        info_layout.addWidget(action_label)
        info_layout.addWidget(time_label)

        layout.addWidget(indicator, alignment=Qt.AlignTop)
        layout.addLayout(info_layout, 1)

        item.setLayout(layout)
        return item

    def update_time(self):
        """Обновление времени"""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%B %d, %Y")
        self.time_label.setText(f"🕐 {time_str}\n📅 {date_str}")

    def logout(self):
        """Выход из аккаунта"""
        self.main_window.current_user = None
        self.main_window.navigate_to(0)

    def load_background(self, image_path):
        """Загрузка фонового изображения"""
        try:
            self.background_pixmap = QPixmap(image_path)
            if self.background_pixmap.isNull():
                raise Exception("Не удалось загрузить изображение")
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            self.background_pixmap = None

    def paintEvent(self, event):
        """Отрисовка фона"""
        painter = QPainter(self)

        if self.background_pixmap and not self.background_pixmap.isNull():
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(15, 23, 42))
            gradient.setColorAt(0.5, QColor(30, 41, 59))
            gradient.setColorAt(1, QColor(51, 65, 85))
            painter.fillRect(self.rect(), gradient)

        painter.end()
