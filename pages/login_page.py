"""
Страница авторизации и регистрации
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QLineEdit, QGraphicsOpacityEffect,
                               QMessageBox, QFrame)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QPixmap, QLinearGradient, QColor


class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_login_mode = True  # True = вход, False = регистрация

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Контейнер с оверлеем
        overlay = QWidget()
        overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 23, 42, 0.80);
            }
        """)

        overlay_layout = QHBoxLayout()
        overlay_layout.setContentsMargins(0, 0, 0, 0)

        # ============= ЛЕВАЯ ЧАСТЬ (информационная) =============
        left_panel = QWidget()
        left_panel.setFixedWidth(500)
        left_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(245, 158, 11, 0.15),
                    stop:1 rgba(249, 115, 22, 0.05));
                border-right: 1px solid rgba(245, 158, 11, 0.3);
            }
        """)

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(50, 80, 50, 80)
        left_layout.setSpacing(30)

        # Иконка
        icon_label = QLabel("🏺")
        icon_label.setAlignment(Qt.AlignLeft)
        icon_label.setStyleSheet("font-size: 80px; background: transparent;")
        left_layout.addWidget(icon_label)

        # Заголовок
        welcome_label = QLabel("Welcome to\nRelicSafe")
        welcome_label.setWordWrap(True)
        welcome_font = QFont("Segoe UI", 36, QFont.Bold)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                background: transparent;
                line-height: 1.2;
            }
        """)
        left_layout.addWidget(welcome_label)

        # Описание
        desc_label = QLabel(
            "AI-powered artifact preservation system for archaeological field work.\n\n"
            "• Real-time material analysis\n"
            "• Automated climate control\n"
            "• Digital cataloging\n"
            "• Field-ready solution"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 14px;
                background: transparent;
                line-height: 1.8;
            }
        """)
        left_layout.addWidget(desc_label)

        left_layout.addStretch()

        # Нижняя информация
        info_label = QLabel("FLL SUBMERGED 2024-2025\nTeam Kazakhstan")
        info_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
                background: transparent;
            }
        """)
        left_layout.addWidget(info_label)

        left_panel.setLayout(left_layout)

        # ============= ПРАВАЯ ЧАСТЬ (форма) =============
        right_panel = QWidget()
        right_panel.setStyleSheet("background: transparent;")

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(80, 60, 80, 60)
        right_layout.setSpacing(0)

        right_layout.addStretch()

        # Форма в центре
        form_container = QWidget()
        form_container.setFixedWidth(400)
        form_container.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 41, 59, 0.6);
                border-radius: 20px;
                border: 1px solid rgba(148, 163, 184, 0.1);
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        # Заголовок формы
        self.form_title = QLabel("Sign In")
        self.form_title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 28, QFont.Bold)
        self.form_title.setFont(title_font)
        self.form_title.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                background: transparent;
                padding-bottom: 10px;
            }
        """)
        form_layout.addWidget(self.form_title)

        # Подзаголовок
        self.form_subtitle = QLabel("Enter your credentials to continue")
        self.form_subtitle.setAlignment(Qt.AlignCenter)
        self.form_subtitle.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 13px;
                background: transparent;
                padding-bottom: 20px;
            }
        """)
        form_layout.addWidget(self.form_subtitle)

        # Поле "Полное имя" (только для регистрации)
        self.fullname_label = QLabel("Full Name")
        self.fullname_label.setStyleSheet("color: #cbd5e1; font-size: 13px; background: transparent;")
        self.fullname_label.hide()
        form_layout.addWidget(self.fullname_label)

        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Enter your full name")
        self.fullname_input.setFixedHeight(45)
        self.fullname_input.hide()
        form_layout.addWidget(self.fullname_input)

        # Поле "Username"
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #cbd5e1; font-size: 13px; background: transparent;")
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(45)
        form_layout.addWidget(self.username_input)

        # Поле "Password"
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #cbd5e1; font-size: 13px; background: transparent;")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        form_layout.addWidget(self.password_input)

        # Стили для полей ввода
        input_style = """
            QLineEdit {
                background-color: rgba(15, 23, 42, 0.8);
                color: #f8fafc;
                border: 2px solid rgba(148, 163, 184, 0.2);
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #f59e0b;
                background-color: rgba(15, 23, 42, 0.95);
            }
        """
        self.username_input.setStyleSheet(input_style)
        self.password_input.setStyleSheet(input_style)
        self.fullname_input.setStyleSheet(input_style)

        form_layout.addSpacing(10)

        # Кнопка действия (Login/Register)
        self.action_button = QPushButton("Sign In")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.setFixedHeight(50)
        self.action_button.clicked.connect(self.on_action_clicked)

        button_font = QFont("Segoe UI", 14, QFont.Bold)
        self.action_button.setFont(button_font)
        self.action_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f59e0b, stop:1 #f97316);
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ea580c, stop:1 #dc2626);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c2410c, stop:1 #b91c1c);
            }
        """)
        form_layout.addWidget(self.action_button)

        form_layout.addSpacing(15)

        # Разделитель
        divider_layout = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet("background-color: rgba(148, 163, 184, 0.2); border: none; height: 1px;")

        or_label = QLabel("OR")
        or_label.setStyleSheet("color: #64748b; font-size: 12px; background: transparent; padding: 0 10px;")

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet("background-color: rgba(148, 163, 184, 0.2); border: none; height: 1px;")

        divider_layout.addWidget(line1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line2)
        form_layout.addLayout(divider_layout)

        form_layout.addSpacing(15)

        # Переключение режима
        switch_container = QWidget()
        switch_container.setStyleSheet("background: transparent;")
        switch_layout = QHBoxLayout()
        switch_layout.setContentsMargins(0, 0, 0, 0)

        self.switch_label = QLabel("Don't have an account?")
        self.switch_label.setStyleSheet("color: #94a3b8; font-size: 13px; background: transparent;")

        self.switch_button = QPushButton("Sign Up")
        self.switch_button.setCursor(Qt.PointingHandCursor)
        self.switch_button.clicked.connect(self.toggle_mode)
        self.switch_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #f59e0b;
                border: none;
                font-size: 13px;
                font-weight: bold;
                text-decoration: underline;
                padding: 0;
            }
            QPushButton:hover {
                color: #ea580c;
            }
        """)

        switch_layout.addStretch()
        switch_layout.addWidget(self.switch_label)
        switch_layout.addWidget(self.switch_button)
        switch_layout.addStretch()
        switch_container.setLayout(switch_layout)
        form_layout.addWidget(switch_container)

        form_container.setLayout(form_layout)

        # Центрирование формы
        form_wrapper = QHBoxLayout()
        form_wrapper.addStretch()
        form_wrapper.addWidget(form_container)
        form_wrapper.addStretch()

        right_layout.addLayout(form_wrapper)
        right_layout.addStretch()

        # Кнопка "Назад"
        back_button = QPushButton("← Back to Start")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(lambda: self.main_window.navigate_to(0))
        back_button.setFixedHeight(40)
        back_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 8px;
                font-size: 13px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: rgba(148, 163, 184, 0.1);
                color: #cbd5e1;
            }
        """)

        back_container = QHBoxLayout()
        back_container.addWidget(back_button)
        back_container.addStretch()
        right_layout.addLayout(back_container)

        right_panel.setLayout(right_layout)

        # Добавление панелей в оверлей
        overlay_layout.addWidget(left_panel)
        overlay_layout.addWidget(right_panel)

        overlay.setLayout(overlay_layout)
        main_layout.addWidget(overlay)

        self.setLayout(main_layout)

        # Загрузка фона
        self.background_pixmap = None
        self.load_background("img.png")

        # Анимация
        self.fade_in_animation()

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

    def fade_in_animation(self):
        """Анимация появления"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def toggle_mode(self):
        """Переключение между входом и регистрацией"""
        self.is_login_mode = not self.is_login_mode

        if self.is_login_mode:
            # Режим входа
            self.form_title.setText("Sign In")
            self.form_subtitle.setText("Enter your credentials to continue")
            self.action_button.setText("Sign In")
            self.switch_label.setText("Don't have an account?")
            self.switch_button.setText("Sign Up")
            self.fullname_label.hide()
            self.fullname_input.hide()
        else:
            # Режим регистрации
            self.form_title.setText("Sign Up")
            self.form_subtitle.setText("Create a new account")
            self.action_button.setText("Create Account")
            self.switch_label.setText("Already have an account?")
            self.switch_button.setText("Sign In")
            self.fullname_label.show()
            self.fullname_input.show()

        # Очистка полей
        self.username_input.clear()
        self.password_input.clear()
        self.fullname_input.clear()

    def on_action_clicked(self):
        """Обработка входа или регистрации"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_message("Error", "Please fill in all fields", QMessageBox.Warning)
            return

        if self.is_login_mode:
            # Вход
            success, result = self.main_window.database.login_user(username, password)
            if success:
                self.main_window.current_user = result
                print(f"Logged in as: {result}")
                self.main_window.navigate_to(2)  # Dashboard
            else:
                self.show_message("Login Failed", result, QMessageBox.Critical)
        else:
            # Регистрация
            full_name = self.fullname_input.text().strip()
            if not full_name:
                self.show_message("Error", "Please enter your full name", QMessageBox.Warning)
                return

            success, message = self.main_window.database.register_user(username, password, full_name)
            if success:
                self.show_message("Success", "Account created successfully! You can now sign in.",
                                  QMessageBox.Information)
                self.toggle_mode()  # Переключить на режим входа
            else:
                self.show_message("Registration Failed", message, QMessageBox.Critical)

    def show_message(self, title, message, icon):
        """Показ диалогового окна"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec()
