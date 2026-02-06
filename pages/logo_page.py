"""
Стартовая страница с логотипом и фоновым изображением
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGraphicsOpacityEffect, QFrame)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QPixmap, QPalette, QBrush, QFont, QPainter

class LogoPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Основной layout на весь экран
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ============= ПОЛУПРОЗРАЧНЫЙ ОВЕРЛЕЙ НА ВЕСЬ ЭКРАН =============
        overlay = QWidget()
        overlay.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 23, 42, 0.75);
            }
        """)

        overlay_layout = QVBoxLayout()
        overlay_layout.setContentsMargins(60, 40, 60, 40)
        overlay_layout.setSpacing(0)

        # ============= ВЕРХНЯЯ ПАНЕЛЬ (Статус-бар) =============
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("background: transparent;")

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(20, 0, 20, 0)

        # Версия приложения
        version_label = QLabel("v1.0.0-beta")
        version_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 11px;
                background: rgba(30, 41, 59, 0.6);
                padding: 6px 12px;
                border-radius: 12px;
            }
        """)

        # Статус системы
        status_container = QWidget()
        status_container.setStyleSheet("background: transparent;")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(15)

        # Индикатор камеры
        camera_status = QLabel("● Camera")
        camera_status.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 11px;
                background: rgba(30, 41, 59, 0.6);
                padding: 6px 12px;
                border-radius: 12px;
            }
        """)

        # Индикатор базы данных
        db_status = QLabel("● Database")
        db_status.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 11px;
                background: rgba(30, 41, 59, 0.6);
                padding: 6px 12px;
                border-radius: 12px;
            }
        """)

        # Индикатор контейнера (не подключен пока)
        container_status = QLabel("○ Container")
        container_status.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 11px;
                background: rgba(30, 41, 59, 0.6);
                padding: 6px 12px;
                border-radius: 12px;
            }
        """)

        status_layout.addWidget(camera_status)
        status_layout.addWidget(db_status)
        status_layout.addWidget(container_status)
        status_container.setLayout(status_layout)

        top_layout.addWidget(version_label)
        top_layout.addStretch()
        top_layout.addWidget(status_container)

        top_bar.setLayout(top_layout)
        overlay_layout.addWidget(top_bar)

        # ============= ЦЕНТРАЛЬНАЯ ЧАСТЬ =============
        overlay_layout.addStretch(1)

        center_content = QWidget()
        center_content.setStyleSheet("background: transparent;")
        center_layout = QVBoxLayout()
        center_layout.setSpacing(20)

        # Иконка
        icon_label = QLabel("🏺")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 110px;
                background: transparent;
                padding: 20px;
            }
        """)
        center_layout.addWidget(icon_label)

        # Заголовок
        title_label = QLabel("RelicSafe")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 64, QFont.Bold)
        title_font.setLetterSpacing(QFont.AbsoluteSpacing, 5)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                background: transparent;
                padding: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }
        """)
        center_layout.addWidget(title_label)

        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedWidth(300)
        line.setStyleSheet("""
            QFrame {
                color: #f59e0b;
                background-color: #f59e0b;
                border: none;
                height: 2px;
            }
        """)

        line_container = QWidget()
        line_container.setStyleSheet("background: transparent;")
        line_layout = QHBoxLayout()
        line_layout.addStretch()
        line_layout.addWidget(line)
        line_layout.addStretch()
        line_container.setLayout(line_layout)
        center_layout.addWidget(line_container)

        center_layout.addSpacing(10)

        # Подзаголовок
        subtitle_label = QLabel("Artifact Conservation System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Segoe UI", 26)
        subtitle_font.setLetterSpacing(QFont.AbsoluteSpacing, 3)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                background: transparent;
                padding: 5px;
            }
        """)
        center_layout.addWidget(subtitle_label)

        center_layout.addSpacing(15)

        # Описание
        description_label = QLabel(
            "AI-powered field preservation solution for archaeological discoveries\n"
            "Real-time material analysis • Climate control • Digital cataloging"
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: #94a3b8;
                background: transparent;
                padding: 15px;
                line-height: 1.8;
            }
        """)
        center_layout.addWidget(description_label)

        center_layout.addSpacing(30)

        # Кнопка
        self.start_button = QPushButton("LET'S GO →")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setFixedSize(240, 70)
        self.start_button.clicked.connect(self.on_start_clicked)

        button_font = QFont("Segoe UI", 18, QFont.Bold)
        button_font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        self.start_button.setFont(button_font)

        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f59e0b, stop:1 #f97316);
                color: white;
                border: 2px solid rgba(245, 158, 11, 0.3);
                border-radius: 35px;
                padding: 0px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ea580c, stop:1 #dc2626);
                border: 2px solid rgba(234, 88, 12, 0.5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c2410c, stop:1 #b91c1c);
            }
        """)

        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        center_layout.addWidget(button_container)

        center_content.setLayout(center_layout)
        overlay_layout.addWidget(center_content)

        overlay_layout.addStretch(1)

        # ============= НИЖНЯЯ ПАНЕЛЬ =============
        bottom_bar = QWidget()
        bottom_bar.setFixedHeight(60)
        bottom_bar.setStyleSheet("background: transparent;")

        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(8)

        # Информация о команде
        footer_label = QLabel("FLL SUBMERGED Season 2025-2026  •  Tidal Tumble")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #64748b;
                background: transparent;
            }
        """)

        # Копирайт
        copyright_label = QLabel("© 2025 Smart Container Project  •  Powered by PySide6 & TensorFlow")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #475569;
                background: transparent;
            }
        """)

        bottom_layout.addWidget(footer_label)
        bottom_layout.addWidget(copyright_label)
        bottom_bar.setLayout(bottom_layout)

        overlay_layout.addWidget(bottom_bar)

        overlay.setLayout(overlay_layout)
        main_layout.addWidget(overlay)

        self.setLayout(main_layout)

        # Установка фона
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
            print("Фоновое изображение загружено успешно")
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            self.background_pixmap = None

    def paintEvent(self, event):
        """Отрисовка фона на весь экран"""
        painter = QPainter(self)

        if self.background_pixmap and not self.background_pixmap.isNull():
            # Растягиваем фон на весь размер виджета
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            # Центрируем изображение
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2

            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            # Fallback: градиентный фон
            painter.fillRect(self.rect(), Qt.black)
            from PySide6.QtGui import QLinearGradient, QColor
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(15, 23, 42))
            gradient.setColorAt(0.5, QColor(30, 41, 59))
            gradient.setColorAt(1, QColor(51, 65, 85))
            painter.fillRect(self.rect(), gradient)

        painter.end()

    def fade_in_animation(self):
        """Анимация плавного появления"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def on_start_clicked(self):
        """Обработчик кнопки LET'S GO"""
        self.main_window.navigate_to(1)  # Переход на LoginPage

