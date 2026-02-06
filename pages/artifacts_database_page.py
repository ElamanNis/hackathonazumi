"""
Страница базы данных артефактов - Premium Gallery
"""

import os
from datetime import datetime

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QScrollArea, QGridLayout,
                               QLineEdit, QComboBox, QMessageBox, QDialog,
                               QGraphicsDropShadowEffect, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPainter, QPixmap, QColor, QLinearGradient, QPen

from models.database import Database

# Константы стилей
COLOR_PRIMARY = "#f59e0b"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#ef4444"
COLOR_INFO = "#3b82f6"
COLOR_WARNING = "#fbbf24"
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_SECONDARY = "#94a3b8"
COLOR_BACKGROUND = "#0f172a"

# Настройки материалов (с иконками и цветами)
MATERIAL_COLORS = {
    'Clay': {'icon': '🏺', 'color': '#d97706'},
    'Glass': {'icon': '💎', 'color': '#06b6d4'},
    'Iron': {'icon': '⚔️', 'color': '#71717a'},
    'Wood': {'icon': '🪵', 'color': '#92400e'},
    'Bronze': {'icon': '🗿', 'color': '#b45309'},
    'Paper': {'icon': '📜', 'color': '#f5f5f4'},
}


# -------------------- UI Components --------------------

class StatCard(QFrame):
    """Карточка статистики"""

    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setFixedSize(200, 120)
        self.color = color
        self.value_label = None  # ← Сохраняем ссылку на label
        self.setup_ui(title, value, icon)
        self.add_shadow()

    def setup_ui(self, title, value, icon):
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(30, 41, 59, 0.9),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 2px solid {self.color};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        # Icon + Title
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 28px;")

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px; font-weight: bold;")

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        layout.addLayout(header)
        layout.addSpacing(10)

        # Value - сохраняем ссылку!
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        self.value_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.value_label)

    def update_value(self, new_value):
        """Обновить значение"""
        if self.value_label:
            self.value_label.setText(str(new_value))

    def add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)



class ArtifactCard(QFrame):
    """Карточка артефакта с фото"""
    clicked = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, artifact_data):
        super().__init__()
        self.artifact_id = artifact_data['id']
        self.data = artifact_data
        self.setFixedSize(280, 380)
        self.setup_ui()
        self.add_shadow()
        self.setCursor(Qt.PointingHandCursor)

    def setup_ui(self):
        material = self.data.get('material', 'Unknown')
        mat_info = MATERIAL_COLORS.get(material, {'icon': '📦', 'color': '#64748b'})

        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.95),
                    stop:1 rgba(15, 23, 42, 0.95));
                border: 2px solid {mat_info['color']};
                border-radius: 20px;
            }}
            QFrame:hover {{
                border: 3px solid {COLOR_PRIMARY};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(40, 51, 69, 0.95),
                    stop:1 rgba(25, 33, 52, 0.95));
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Photo
        photo_frame = QFrame()
        photo_frame.setFixedSize(250, 200)
        photo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-radius: 12px;
                border: 2px solid {mat_info['color']};
            }}
        """)

        photo_layout = QVBoxLayout(photo_frame)
        photo_layout.setContentsMargins(0, 0, 0, 0)

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("border: none; background: transparent;")

        # Загрузка фото
        photo_path = self.data.get('photo_path', '')
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(250, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled)
            else:
                self.photo_label.setText("📷\nNo Image")
                self.photo_label.setStyleSheet("color: #64748b; font-size: 18px; border: none;")
        else:
            self.photo_label.setText("📷\nNo Image")
            self.photo_label.setStyleSheet("color: #64748b; font-size: 18px; border: none;")

        photo_layout.addWidget(self.photo_label)
        layout.addWidget(photo_frame)

        # Material + Badge
        header = QHBoxLayout()

        material_lbl = QLabel(f"{mat_info['icon']} {material}")
        material_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        material_lbl.setStyleSheet(f"color: {mat_info['color']}; background: transparent; border: none;")

        header.addWidget(material_lbl)
        header.addStretch()

        # Manual override badge
        if self.data.get('manual_override'):
            badge = QLabel("✏️")
            badge.setToolTip("Manual Override")
            badge.setStyleSheet(f"color: {COLOR_WARNING}; font-size: 20px; border: none;")
            header.addWidget(badge)
        else:
            badge = QLabel("🤖")
            badge.setToolTip("AI Classified")
            badge.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 20px; border: none;")
            header.addWidget(badge)

        layout.addLayout(header)

        # Info
        info_text = f"ID: #{self.artifact_id} | Confidence: {self.data.get('confidence', 0):.1f}%\n"
        info_text += f"📅 {self.data.get('date_found', 'N/A')} {self.data.get('time_found', '')}\n"
        info_text += f"📍 {self.data.get('location', 'Unknown')}"

        info_lbl = QLabel(info_text)
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(info_lbl)

        # Buttons
        btn_layout = QHBoxLayout()

        view_btn = QPushButton("👁 View")
        delete_btn = QPushButton("🗑️")

        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_INFO};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #2563eb; }}
        """)

        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_DANGER};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #dc2626; }}
        """)

        delete_btn.setFixedWidth(50)

        view_btn.clicked.connect(lambda: self.clicked.emit(self.artifact_id))
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.artifact_id))

        btn_layout.addWidget(view_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

    def add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.artifact_id)


# -------------------- Detail Dialog --------------------

class ArtifactDetailDialog(QDialog):
    """Диалог с детальной информацией об артефакте"""

    def __init__(self, artifact_data, parent=None):
        super().__init__(parent)
        self.data = artifact_data
        self.setWindowTitle(f"Artifact #{artifact_data['id']} Details")
        self.setFixedSize(700, 600)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLOR_BACKGROUND};
            }}
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        material = self.data.get('material', 'Unknown')
        mat_info = MATERIAL_COLORS.get(material, {'icon': '📦', 'color': '#64748b'})

        title = QLabel(f"{mat_info['icon']} {material} - Artifact #{self.data['id']}")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {mat_info['color']};")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Photo
        photo_path = self.data.get('photo_path', '')
        if photo_path and os.path.exists(photo_path):
            photo_label = QLabel()
            photo_label.setAlignment(Qt.AlignCenter)
            photo_label.setStyleSheet("background-color: #000; border-radius: 12px; padding: 10px;")

            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                photo_label.setPixmap(scaled)
                layout.addWidget(photo_label)

        # Info Grid
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border-radius: 12px;
                padding: 20px;
            }
        """)

        info_layout = QGridLayout(info_frame)
        info_layout.setSpacing(15)

        details = [
            ("🆔 ID:", f"#{self.data['id']}"),
            ("📊 Confidence:", f"{self.data.get('confidence', 0):.1f}%"),
            ("🤖 Classification:", "Manual Override" if self.data.get('manual_override') else "AI Detected"),
            ("📅 Date Found:", self.data.get('date_found', 'N/A')),
            ("⏰ Time Found:", self.data.get('time_found', 'N/A')),
            ("📍 Location:", self.data.get('location', 'Unknown')),
            ("🔬 Project:", self.data.get('project', 'N/A')),
            ("👤 Archaeologist:", self.data.get('archaeologist', 'N/A')),
            ("📏 Depth:", f"{self.data.get('depth', 0):.2f} m"),
            ("🗂️ Container:", f"#{self.data.get('container_id', 'N/A')}"),
        ]

        row = 0
        for label_text, value_text in details:
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-weight: bold;")

            value = QLabel(str(value_text))
            value.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            value.setWordWrap(True)

            info_layout.addWidget(label, row, 0, Qt.AlignRight)
            info_layout.addWidget(value, row, 1)
            row += 1

        # Description
        if self.data.get('description'):
            desc_label = QLabel("📝 Description:")
            desc_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-weight: bold;")
            info_layout.addWidget(desc_label, row, 0, Qt.AlignRight | Qt.AlignTop)

            desc_value = QLabel(self.data['description'])
            desc_value.setWordWrap(True)
            desc_value.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            info_layout.addWidget(desc_value, row, 1)

        layout.addWidget(info_frame)

        # Close Button
        close_btn = QPushButton("✖ Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_DANGER};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #dc2626; }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


# -------------------- Main Page --------------------

class ArtifactsDatabasePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = Database()
        self.artifacts = []
        self.filtered_artifacts = []

        # Background
        self.background_pixmap = None
        self.load_background("img.png")

        self.setup_ui()
        self.load_artifacts()

    def load_background(self, path):
        try:
            if os.path.exists(path):
                self.background_pixmap = QPixmap(path)
        except Exception as e:
            print(f"✗ Ошибка загрузки фона: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.background_pixmap and not self.background_pixmap.isNull():
            scaled = self.background_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        # Полупрозрачный оверлей
        painter.fillRect(self.rect(), QColor(15, 23, 42, int(255 * 0.88)))
        painter.end()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()

        # Back Button
        back_btn = QPushButton("← Back")
        back_btn.setFixedSize(120, 45)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(30, 41, 59, 0.8);
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid {COLOR_PRIMARY};
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(245, 158, 11, 0.2);
            }}
        """)
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn)

        header_layout.addStretch()

        # Title
        title = QLabel("🏛️ ARTIFACTS DATABASE")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setStyleSheet(f"""
            color: {COLOR_PRIMARY};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(245, 158, 11, 0.2),
                stop:0.5 rgba(245, 158, 11, 0.3),
                stop:1 rgba(245, 158, 11, 0.2));
            border-radius: 16px;
            padding: 15px 40px;
            border: 3px solid {COLOR_PRIMARY};
        """)
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title, 1)

        header_layout.addStretch()

        # Refresh Button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(45, 45)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setToolTip("Refresh Database")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 20px;
            }}
            QPushButton:hover {{ background-color: #059669; }}
        """)
        refresh_btn.clicked.connect(self.load_artifacts)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # Statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.stat_total = StatCard("Total Artifacts", "0", "📦", COLOR_INFO)
        self.stat_ai = StatCard("AI Classified", "0", "🤖", COLOR_SUCCESS)
        self.stat_manual = StatCard("Manual Override", "0", "✏️", COLOR_WARNING)
        self.stat_recent = StatCard("Today", "0", "📅", COLOR_PRIMARY)

        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_ai)
        stats_layout.addWidget(self.stat_manual)
        stats_layout.addWidget(self.stat_recent)
        stats_layout.addStretch()

        main_layout.addLayout(stats_layout)

        # Filters
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border-radius: 16px;
                padding: 20px;
                border: 2px solid rgba(245, 158, 11, 0.3);
            }
        """)

        filter_layout = QHBoxLayout(filter_frame)

        # Search
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        filter_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, material, location...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(0, 0, 0, 0.3);
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """)
        self.search_input.textChanged.connect(self.filter_artifacts)
        filter_layout.addWidget(self.search_input, 1)

        # Material Filter
        filter_label = QLabel("📋 Material:")
        filter_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        filter_layout.addWidget(filter_label)

        self.material_filter = QComboBox()
        self.material_filter.addItems(["All Materials"] + list(MATERIAL_COLORS.keys()))
        self.material_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 0.3);
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-width: 150px;
            }}
        """)
        self.material_filter.currentTextChanged.connect(self.filter_artifacts)
        filter_layout.addWidget(self.material_filter)

        # Classification Filter
        class_label = QLabel("🤖 Type:")
        class_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        filter_layout.addWidget(class_label)

        self.class_filter = QComboBox()
        self.class_filter.addItems(["All", "AI Only", "Manual Only"])
        self.class_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(0, 0, 0, 0.3);
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-width: 130px;
            }}
        """)
        self.class_filter.currentTextChanged.connect(self.filter_artifacts)
        filter_layout.addWidget(self.class_filter)

        main_layout.addWidget(filter_frame)

        # Gallery
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(30, 41, 59, 0.5);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(245, 158, 11, 0.7);
                border-radius: 6px;
            }
        """)

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(25)
        self.gallery_layout.setContentsMargins(10, 10, 10, 10)

        scroll.setWidget(self.gallery_widget)
        main_layout.addWidget(scroll)

    def load_artifacts(self):
        """Загрузка артефактов из БД"""
        try:
            self.artifacts = self.db.get_all_artifacts()
            self.filtered_artifacts = self.artifacts.copy()

            print(f"✓ Загружено артефактов: {len(self.artifacts)}")

            self.update_statistics()
            self.display_artifacts()

        except Exception as e:
            print(f"✗ Ошибка загрузки артефактов: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load artifacts:\n{str(e)}")

    def update_statistics(self):
        """Обновление статистики"""
        total = len(self.artifacts)
        ai_count = sum(1 for a in self.artifacts if not a.get('manual_override'))
        manual_count = sum(1 for a in self.artifacts if a.get('manual_override'))

        today = datetime.now().strftime("%Y-%m-%d")
        today_count = sum(1 for a in self.artifacts if a.get('date_found', '') == today)

        # Используем новый метод update_value()
        self.stat_total.update_value(total)
        self.stat_ai.update_value(ai_count)
        self.stat_manual.update_value(manual_count)
        self.stat_recent.update_value(today_count)

    def filter_artifacts(self):
        """Фильтрация артефактов"""
        search_text = self.search_input.text().lower()
        material = self.material_filter.currentText()
        classification = self.class_filter.currentText()

        self.filtered_artifacts = []

        for artifact in self.artifacts:
            # Search filter
            if search_text:
                searchable = f"{artifact['id']} {artifact.get('material', '')} {artifact.get('location', '')}".lower()
                if search_text not in searchable:
                    continue

            # Material filter
            if material != "All Materials" and artifact.get('material') != material:
                continue

            # Classification filter
            if classification == "AI Only" and artifact.get('manual_override'):
                continue
            elif classification == "Manual Only" and not artifact.get('manual_override'):
                continue

            self.filtered_artifacts.append(artifact)

        self.display_artifacts()

    def display_artifacts(self):
        """Отображение артефактов в галерее"""
        # Очистка галереи
        while self.gallery_layout.count():
            item = self.gallery_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.filtered_artifacts:
            no_data = QLabel("📭 No artifacts found")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 24px; padding: 50px;")
            self.gallery_layout.addWidget(no_data, 0, 0, 1, 3)
            return

        # Отображение карточек (3 колонки)
        row = 0
        col = 0

        for artifact in self.filtered_artifacts:
            card = ArtifactCard(artifact)
            card.clicked.connect(self.show_artifact_details)
            card.delete_requested.connect(self.delete_artifact)

            self.gallery_layout.addWidget(card, row, col)

            col += 1
            if col >= 3:
                col = 0
                row += 1

    def show_artifact_details(self, artifact_id):
        """Показать детали артефакта"""
        artifact = next((a for a in self.artifacts if a['id'] == artifact_id), None)
        if artifact:
            dialog = ArtifactDetailDialog(artifact, self)
            dialog.exec()

    def delete_artifact(self, artifact_id):
        """Удалить артефакт"""
        reply = QMessageBox.question(
            self, "Delete Artifact",
            f"Are you sure you want to delete Artifact #{artifact_id}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Удаляем фото если есть
                artifact = next((a for a in self.artifacts if a['id'] == artifact_id), None)
                if artifact and artifact.get('photo_path'):
                    if os.path.exists(artifact['photo_path']):
                        os.remove(artifact['photo_path'])
                        print(f"✓ Фото удалено: {artifact['photo_path']}")

                # Удаляем из БД
                success = self.db.delete_artifact(artifact_id)

                if success:
                    QMessageBox.information(self, "Success", f"Artifact #{artifact_id} deleted successfully")
                    self.load_artifacts()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete artifact")

            except Exception as e:
                print(f"✗ Ошибка удаления: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{str(e)}")

    def go_back(self):
        """Вернуться назад"""
        # Замени на правильный индекс страницы
        self.main_window.stacked_widget.setCurrentIndex(2)  # Например, страница контейнеров
