"""
Страница управления контейнерами - ESP32 Direct Connection (без HTTP)
"""

import os
import socket
import cv2
import re
from datetime import datetime

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QComboBox,
                               QTabWidget, QMessageBox, QTableWidget,
                               QTableWidgetItem, QHeaderView, QDoubleSpinBox)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QPainter, QPixmap, QColor, QImage

from models.classifier import ArtifactClassifier
from models.database import Database

# Константы стилей
COLOR_PRIMARY = "#f59e0b"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#ef4444"
COLOR_WARNING = "#fbbf24"
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_SECONDARY = "#94a3b8"

# Настройки материалов
MATERIAL_SETTINGS = {
    'Clay': {'temp': 20.0, 'hum': 45.0, 'spray': 'Water', 'desc': 'Stable humidity prevents cracking', 'icon': '🏺', 'color': '#d97706'},
    'Glass': {'temp': 20.0, 'hum': 40.0, 'spray': 'None', 'desc': 'Prevent weeping glass syndrome', 'icon': '💎', 'color': '#06b6d4'},
    'Iron': {'temp': 5.0, 'hum': 10.0, 'spray': 'BTA', 'desc': 'Critical low humidity required', 'icon': '⚔️', 'color': '#71717a'},
    'Wood': {'temp': 18.0, 'hum': 55.0, 'spray': 'Water', 'desc': 'Prevent drying/cracking', 'icon': '🪵', 'color': '#92400e'},
    'Bronze': {'temp': 5.0, 'hum': 12.0, 'spray': 'BTA', 'desc': 'Prevent bronze disease', 'icon': '🗿', 'color': '#b45309'},
    'Paper': {'temp': 18.0, 'hum': 50.0, 'spray': 'None', 'desc': 'Avoid light/humidity changes', 'icon': '📜', 'color': '#f5f5f4'},
}


# ========== ESP32 DATA FETCHER (БЕЗ HTTP) ==========
class DataFetcher(QThread):
    """Поток для получения данных с ESP32 через прямое подключение"""
    data_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, ip):
        super().__init__()
        self.ip = ip
        self.running = True

    def run(self):
        while self.running:
            try:
                # Прямое подключение к ESP32 через сокет
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.ip, 80))

                # Отправляем GET запрос
                request = f"GET / HTTP/1.1\r\nHost: {self.ip}\r\nConnection: close\r\n\r\n"
                sock.send(request.encode())

                # Получаем ответ
                response = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk

                sock.close()

                # Парсим данные
                html = response.decode('utf-8', errors='ignore')
                data = self.parse_esp32_data(html)
                self.data_received.emit(data)

            except socket.timeout:
                self.error_occurred.emit("Timeout")
            except ConnectionRefusedError:
                self.error_occurred.emit("Connection refused")
            except Exception as e:
                self.error_occurred.emit(f"Error: {str(e)}")

            self.msleep(1000)  # Задержка 1 секунда между запросами

    def parse_esp32_data(self, html):
        """Парсинг HTML от ESP32"""
        data = {
            'temp': 0.0,
            'hum': 0.0,
            'target_temp': 0.0,
            'target_hum': 0.0,
            'relay_temp': 'OFF',
            'relay_hum': 'OFF',
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }

        # Убираем теги
        clean = re.sub(r'<[^>]+>', ' ', html)
        clean = re.sub(r'\s+', ' ', clean)

        # Парсим значения
        m = re.search(r'Текущая температура:\s*([0-9]+\.?[0-9]*)', clean, re.IGNORECASE)
        if m:
            data['temp'] = float(m.group(1))

        m = re.search(r'Текущая влажность:\s*([0-9]+\.?[0-9]*)', clean, re.IGNORECASE)
        if m:
            data['hum'] = float(m.group(1))

        m = re.search(r'Нужная температура:\s*([0-9]+\.?[0-9]*)', clean, re.IGNORECASE)
        if m:
            data['target_temp'] = float(m.group(1))

        m = re.search(r'Нужная влажность:\s*([0-9]+\.?[0-9]*)', clean, re.IGNORECASE)
        if m:
            data['target_hum'] = float(m.group(1))

        m = re.search(r'Реле температуры:\s*(ВКЛ|ВЫКЛ)', clean, re.IGNORECASE)
        if m:
            data['relay_temp'] = 'ON' if 'ВКЛ' in m.group(1).upper() else 'OFF'

        m = re.search(r'Реле влажности:\s*(ВКЛ|ВЫКЛ)', clean, re.IGNORECASE)
        if m:
            data['relay_hum'] = 'ON' if 'ВКЛ' in m.group(1).upper() else 'OFF'

        return data

    def stop(self):
        self.running = False


# -------------------- UI Components --------------------

class StatusBadge(QLabel):
    def __init__(self, text, color):
        super().__init__(text)
        self.setStyleSheet(f"""
            background-color: {color}20;
            color: {color};
            border: 1px solid {color}40;
            border-radius: 6px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 11px;
        """)


class ContainerCard(QFrame):
    selected = Signal(int)

    def __init__(self, container_id):
        super().__init__()
        self.container_id = container_id
        self.is_selected = False
        self.setObjectName("card")
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(140)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        title = QLabel(f"Container #{self.container_id}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")


        self.status_badge = StatusBadge("OFFLINE", COLOR_DANGER)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_badge)
        layout.addLayout(header)

        # Info
        self.info_label = QLabel("No artifact")
        self.info_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.info_label)

        # Metrics
        metrics = QHBoxLayout()
        self.temp_label = QLabel("🌡️ --°C")
        self.hum_label = QLabel("💧 --%")

        for lbl in [self.temp_label, self.hum_label]:
            lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 13px;")
            metrics.addWidget(lbl)
        metrics.addStretch()
        layout.addLayout(metrics)

        self.update_style()

    def update_data(self, temp, hum, status, material=None):
        self.temp_label.setText(f"🌡️ {temp:.1f}°C")
        self.hum_label.setText(f"💧 {hum:.1f}%")

        if status == "active":
            self.status_badge.setText("ACTIVE")
            self.status_badge.setStyleSheet(f"background-color: {COLOR_SUCCESS}20; color: {COLOR_SUCCESS}; border: 1px solid {COLOR_SUCCESS}40; border-radius: 6px; padding: 4px 8px; font-weight: bold; font-size: 11px;")
        elif status == "offline":
            self.status_badge.setText("OFFLINE")
            self.status_badge.setStyleSheet(f"background-color: {COLOR_DANGER}20; color: {COLOR_DANGER}; border: 1px solid {COLOR_DANGER}40; border-radius: 6px; padding: 4px 8px; font-weight: bold; font-size: 11px;")
        else:
            self.status_badge.setText("STANDBY")
            self.status_badge.setStyleSheet(f"background-color: {COLOR_WARNING}20; color: {COLOR_WARNING}; border: 1px solid {COLOR_WARNING}40; border-radius: 6px; padding: 4px 8px; font-weight: bold; font-size: 11px;")

        if material:
            icon = MATERIAL_SETTINGS.get(material, {}).get('icon', '📦')
            self.info_label.setText(f"{icon} {material}")
        else:
            self.info_label.setText("Empty")

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        border = f"2px solid {COLOR_PRIMARY}" if self.is_selected else "1px solid rgba(255,255,255,0.1)"
        bg = "rgba(245, 158, 11, 0.15)" if self.is_selected else "rgba(30, 41, 59, 0.7)"

        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {bg};
                border: {border};
                border-radius: 16px;
            }}
            QFrame#card:hover {{
                background-color: rgba(245, 158, 11, 0.2);
            }}
        """)

    def mousePressEvent(self, event):
        self.selected.emit(self.container_id)


# -------------------- Main Page --------------------

class ContainerManagementPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = Database()

        try:
            self.classifier = ArtifactClassifier()
            print("✓ AI classifier loaded")
        except Exception as e:
            print(f"✗ AI classifier error: {e}")
            self.classifier = None

        # State
        self.selected_id = 1
        self.containers = {
            1: {
                "ip": "192.168.4.1",
                "status": "offline",
                "temp": 0.0, "hum": 0.0,
                "target_temp": 0.0, "target_hum": 0.0,
                "relay_temp": "OFF", "relay_hum": "OFF",
                "material": None, "artifact_id": None
            }
        }

        self.camera = None
        self.camera_timer = None
        self.captured_frame = None

        # ESP32 Data Fetcher
        self.data_fetcher = None

        # Background
        self.background_pixmap = None
        self.load_background("img.png")

        self.setup_ui()

        # Запускаем подключение к ESP32
        self.start_connection()

    def start_connection(self):
        """Запуск потока для получения данных с ESP32"""
        for cid, cont in self.containers.items():
            ip = cont['ip']

            self.data_fetcher = DataFetcher(ip)
            self.data_fetcher.data_received.connect(lambda data, c=cid: self.update_container_data(c, data))
            self.data_fetcher.error_occurred.connect(lambda err, c=cid: self.handle_connection_error(c, err))
            self.data_fetcher.start()

            print(f"🔄 Started connection to {ip}")

    def update_container_data(self, container_id, data):
        """Обновление данных контейнера"""
        cont = self.containers[container_id]

        cont['temp'] = data['temp']
        cont['hum'] = data['hum']
        cont['target_temp'] = data['target_temp']
        cont['target_hum'] = data['target_hum']
        cont['relay_temp'] = data['relay_temp']
        cont['relay_hum'] = data['relay_hum']

        cont['status'] = "active" if cont['artifact_id'] else "standby"

        # Обновляем UI
        if container_id in self.cards:
            self.cards[container_id].update_data(cont['temp'], cont['hum'], cont['status'], cont['material'])

        if container_id == self.selected_id:
            self.sensor_temp.findChild(QLabel, "value").setText(f"{cont['temp']:.1f}°C")
            self.sensor_hum.findChild(QLabel, "value").setText(f"{cont['hum']:.1f}%")
            self.sensor_solar.findChild(QLabel, "value").setText("94%")

            mat_text = cont['material'] if cont['material'] else "None"
            self.sensor_artifact.findChild(QLabel, "value").setText(mat_text)

            fan_color = COLOR_SUCCESS if cont['relay_temp'] == 'ON' else "#94a3b8"
            self.relay_fan_status.setText(f"❄️ Fan: {cont['relay_temp']}")
            self.relay_fan_status.setStyleSheet(f"color: {fan_color}; font-weight: bold; font-size: 16px; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;")

            neb_color = COLOR_SUCCESS if cont['relay_hum'] == 'ON' else "#94a3b8"
            self.relay_nebu_status.setText(f"🌫️ Nebulizer: {cont['relay_hum']}")
            self.relay_nebu_status.setStyleSheet(f"color: {neb_color}; font-weight: bold; font-size: 16px; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;")

    def handle_connection_error(self, container_id, error_msg):
        """Обработка ошибок подключения"""
        cont = self.containers[container_id]
        cont['status'] = "offline"

        if container_id in self.cards:
            self.cards[container_id].update_data(cont['temp'], cont['hum'], "offline", cont['material'])

    def load_background(self, path):
        try:
            self.background_pixmap = QPixmap(path)
            if self.background_pixmap.isNull():
                print(f"⚠ Не удалось загрузить {path}")
        except Exception as e:
            print(f"✗ Ошибка фона: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.background_pixmap and not self.background_pixmap.isNull():
            scaled = self.background_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        painter.fillRect(self.rect(), QColor(15, 23, 42, int(255 * 0.85)))
        painter.end()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)


        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(350)
        sidebar.setStyleSheet("background-color: transparent; border-right: 1px solid rgba(255,255,255,0.1);")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)

        title = QLabel("SMART\nCONTAINERS")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(20)
        back_btn = QPushButton("← Back to Menu")
        back_btn.setFixedHeight(45)
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
                    background-color: rgba(245, 158, 11, 0.3);
                    border: 2px solid {COLOR_PRIMARY};
                }}
            """)
        back_btn.clicked.connect(self.go_back)
        sidebar_layout.addWidget(back_btn)
        sidebar_layout.addSpacing(10)

        self.cards = {}
        for cid in self.containers.keys():
            card = ContainerCard(cid)
            card.selected.connect(self.on_card_selected)
            sidebar_layout.addWidget(card)
            self.cards[cid] = card

        sidebar_layout.addStretch()

        # Main Content
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)

        self.header_title = QLabel("Container #1")
        self.header_title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.header_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        content_layout.addWidget(self.header_title)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: transparent; }}
            QTabBar::tab {{
                background: transparent;
                color: {COLOR_TEXT_SECONDARY};
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLOR_PRIMARY};
                border-bottom: 2px solid {COLOR_PRIMARY};
            }}
        """)

        self.overview_tab = self.create_overview_tab()
        self.control_tab = self.create_control_tab()
        self.scan_tab = self.create_scan_tab()

        self.tabs.addTab(self.overview_tab, "📊 OVERVIEW")
        self.tabs.addTab(self.control_tab, "⚙️ CONTROL")
        self.tabs.addTab(self.scan_tab, "📸 AI SCAN")

        content_layout.addWidget(self.tabs)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

    def create_overview_tab(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(20)

        row1 = QHBoxLayout()

        self.sensor_temp = self.create_sensor_card("Temperature", "0.0°C", "🌡️", "#ef4444")
        self.sensor_hum = self.create_sensor_card("Humidity", "0.0%", "💧", "#3b82f6")
        self.sensor_solar = self.create_sensor_card("Solar", "0%", "☀️", "#f59e0b")
        self.sensor_artifact = self.create_sensor_card("Artifact Type", "None", "📦", "#a855f7")

        row1.addWidget(self.sensor_temp)
        row1.addWidget(self.sensor_hum)
        row1.addWidget(self.sensor_solar)
        row1.addWidget(self.sensor_artifact)

        layout.addLayout(row1)

        status_group = QFrame()
        status_group.setStyleSheet("background-color: rgba(30, 41, 59, 0.7); border-radius: 16px; padding: 20px;")
        status_layout = QHBoxLayout(status_group)

        self.relay_fan_status = QLabel("❄️ Fan: OFF")
        self.relay_nebu_status = QLabel("🌫️ Nebulizer: OFF")

        for lbl in [self.relay_fan_status, self.relay_nebu_status]:
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #94a3b8; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px;")
            status_layout.addWidget(lbl)

        layout.addWidget(status_group)

        table_label = QLabel("📋 Material Settings")
        table_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        table_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; margin-top: 10px;")
        layout.addWidget(table_label)

        self.rec_table = QTableWidget()
        self.rec_table.setColumnCount(4)
        self.rec_table.setHorizontalHeaderLabels(["Material", "Temp", "Humidity", "Spray"])
        self.rec_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rec_table.verticalHeader().setVisible(False)
        self.rec_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: rgba(30, 41, 59, 0.7);
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 12px;
                gridline-color: rgba(255,255,255,0.1);
            }}
            QHeaderView::section {{
                background-color: rgba(0,0,0,0.3);
                color: {COLOR_PRIMARY};
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
        """)

        self.update_material_table(None)
        layout.addWidget(self.rec_table)

        self.rec_card = QFrame()
        self.rec_card.setStyleSheet("background-color: rgba(30, 41, 59, 0.7); border-radius: 16px; padding: 20px; border-left: 4px solid #f59e0b;")
        rec_layout = QVBoxLayout(self.rec_card)

        rec_title = QLabel("💡 Conservation Recommendations")
        rec_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        rec_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        rec_layout.addWidget(rec_title)

        self.rec_text = QLabel("Select an artifact to view recommendations")
        self.rec_text.setWordWrap(True)
        self.rec_text.setStyleSheet("color: #94a3b8; font-size: 14px;")
        rec_layout.addWidget(self.rec_text)

        layout.addWidget(self.rec_card)
        layout.addStretch()
        return page

    def update_material_table(self, selected_material):
        if selected_material:
            self.rec_table.setRowCount(1)
            sets = MATERIAL_SETTINGS.get(selected_material, MATERIAL_SETTINGS['Clay'])
            self.rec_table.setItem(0, 0, QTableWidgetItem(f"{sets['icon']} {selected_material}"))
            self.rec_table.setItem(0, 1, QTableWidgetItem(f"{sets['temp']}°C"))
            self.rec_table.setItem(0, 2, QTableWidgetItem(f"{sets['hum']}%"))
            self.rec_table.setItem(0, 3, QTableWidgetItem(sets['spray']))
        else:
            self.rec_table.setRowCount(len(MATERIAL_SETTINGS))
            for i, (mat, sets) in enumerate(MATERIAL_SETTINGS.items()):
                self.rec_table.setItem(i, 0, QTableWidgetItem(f"{sets['icon']} {mat}"))
                self.rec_table.setItem(i, 1, QTableWidgetItem(f"{sets['temp']}°C"))
                self.rec_table.setItem(i, 2, QTableWidgetItem(f"{sets['hum']}%"))
                self.rec_table.setItem(i, 3, QTableWidgetItem(sets['spray']))

        self.rec_table.setFixedHeight(80 if selected_material else 250)

    def create_sensor_card(self, title, value, icon, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 41, 59, 0.7);
                border-radius: 16px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()

        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        val_lbl.setObjectName("value")

        layout.addLayout(header)
        layout.addWidget(val_lbl)

        return card

    def create_control_tab(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)

        panel = QFrame()
        panel.setStyleSheet("background-color: rgba(30, 41, 59, 0.7); border-radius: 16px; padding: 30px;")
        panel_layout = QVBoxLayout(panel)

        title = QLabel("🛠️ Manual Configuration")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        panel_layout.addWidget(title)
        panel_layout.addSpacing(20)

        self.temp_input = self.create_spinbox("Target Temperature", "°C", 0, 50, 20)
        panel_layout.addLayout(self.temp_input['layout'])

        self.hum_input = self.create_spinbox("Target Humidity", "%", 0, 100, 50)
        panel_layout.addLayout(self.hum_input['layout'])

        spray_layout = QHBoxLayout()
        spray_label = QLabel("Spray Type:")
        spray_label.setStyleSheet("color: #cbd5e1; font-size: 14px;")
        self.spray_combo = QComboBox()
        self.spray_combo.addItems(["None", "Water", "BTA", "Alcohol"])
        self.spray_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(0,0,0,0.3);
                color: white;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        spray_layout.addWidget(spray_label)
        spray_layout.addWidget(self.spray_combo)
        panel_layout.addLayout(spray_layout)

        panel_layout.addSpacing(30)

        apply_btn = QPushButton("APPLY SETTINGS")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #d97706; }}
        """)
        apply_btn.clicked.connect(self.apply_settings)
        panel_layout.addWidget(apply_btn)

        layout.addWidget(panel)
        layout.addStretch()
        return page

    def create_scan_tab(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)

        self.camera_view = QLabel("Camera Offline")
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("background-color: black; border-radius: 16px; color: #64748b;")
        self.camera_view.setFixedSize(640, 480)
        layout.addWidget(self.camera_view, alignment=Qt.AlignCenter)

        controls = QHBoxLayout()

        self.btn_start = QPushButton("▶ START CAMERA")
        self.btn_capture = QPushButton("📸 SCAN & ANALYZE")
        self.btn_capture.setEnabled(False)

        for btn in [self.btn_start, self.btn_capture]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(30, 41, 59, 0.7);
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid rgba(255,255,255,0.1);
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: rgba(255,255,255,0.1); }}
            """)
            controls.addWidget(btn)

        self.btn_start.clicked.connect(self.toggle_camera)
        self.btn_capture.clicked.connect(self.analyze_artifact)

        layout.addLayout(controls)

        override_layout = QHBoxLayout()
        override_label = QLabel("⚠️ AI Correction:")
        override_label.setStyleSheet("color: #f59e0b; font-weight: bold;")

        self.manual_material = QComboBox()
        self.manual_material.addItems(["Auto Detect"] + list(MATERIAL_SETTINGS.keys()))
        self.manual_material.setStyleSheet("""
            QComboBox {
                background-color: rgba(30, 41, 59, 0.7);
                color: white;
                padding: 8px;
                border-radius: 6px;
                min-width: 150px;
            }
        """)

        override_layout.addStretch()
        override_layout.addWidget(override_label)
        override_layout.addWidget(self.manual_material)
        override_layout.addStretch()

        layout.addLayout(override_layout)
        layout.addStretch()
        return page

    def create_spinbox(self, label, suffix, min_val, max_val, val):
        layout = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #cbd5e1; font-size: 14px;")

        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(val)
        spin.setSuffix(f" {suffix}")
        spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: rgba(0,0,0,0.3);
                color: {COLOR_PRIMARY};
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }}
        """)

        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(spin)
        return {'layout': layout, 'widget': spin}

    def on_card_selected(self, cid):
        self.selected_id = cid
        for c_id, card in self.cards.items():
            card.set_selected(c_id == cid)
        self.header_title.setText(f"Container #{cid}")

        cont = self.containers[cid]
        self.temp_input['widget'].setValue(cont['target_temp'])
        self.hum_input['widget'].setValue(cont['target_hum'])

        self.update_material_table(cont['material'])
        self.update_recommendations(cont['material'])

    def update_recommendations(self, material):
        if material and material in MATERIAL_SETTINGS:
            sets = MATERIAL_SETTINGS[material]
            text = f"{sets['icon']} <b>{material}</b><br><br>"
            text += f"<b>Recommended Settings:</b><br>"
            text += f"• Temperature: {sets['temp']}°C<br>"
            text += f"• Humidity: {sets['hum']}%<br>"
            text += f"• Spray: {sets['spray']}<br><br>"
            text += f"<i>{sets['desc']}</i>"
            self.rec_text.setText(text)
        else:
            self.rec_text.setText("⚠️ No artifact detected yet. Scan an artifact to view specific recommendations.")

    def apply_settings(self, auto=False):
        """Отправка настроек на ESP32"""
        if not auto:
            temp = self.temp_input['widget'].value()
            hum = self.hum_input['widget'].value()
        else:
            temp = self.containers[self.selected_id]['target_temp']
            hum = self.containers[self.selected_id]['target_hum']

        cont = self.containers[self.selected_id]
        ip = cont['ip']

        try:
            # Прямое подключение через сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((ip, 80))

            # Отправляем GET запрос с параметрами
            path = f"/?setTemp={temp}&setHum={hum}"
            request = f"GET {path} HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())

            # Получаем ответ
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk

            sock.close()

            print(f"✓ Настройки отправлены: {temp}°C, {hum}%")
            if not auto:
                QMessageBox.information(self, "Success",
                                        f"Settings sent to ESP32:\n\nTemp: {temp}°C\nHumidity: {hum}%")

        except Exception as e:
            print(f"✗ Ошибка отправки: {e}")
            if not auto:
                QMessageBox.warning(self, "Error", f"Failed to send:\n{str(e)}")

    def toggle_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(1)
            if not self.camera.isOpened():
                QMessageBox.warning(self, "Error", "Cannot open camera")
                self.camera = None
                return

            self.camera_timer = QTimer()
            self.camera_timer.timeout.connect(self.update_camera_frame)
            self.camera_timer.start(30)
            self.btn_start.setText("⏹ STOP")
            self.btn_capture.setEnabled(True)
        else:
            self.camera_timer.stop()
            self.camera.release()
            self.camera = None
            self.camera_view.setText("Camera Offline")
            self.btn_start.setText("▶ START CAMERA")
            self.btn_capture.setEnabled(False)

    def update_camera_frame(self):
        ret, frame = self.camera.read()
        if ret:
            self.captured_frame = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.camera_view.setPixmap(QPixmap.fromImage(img).scaled(640, 480, Qt.KeepAspectRatio))

    def analyze_artifact(self):
        if self.captured_frame is None:
            QMessageBox.warning(self, "Error", "No image captured")
            return

        if self.classifier is None:
            QMessageBox.warning(self, "Error", "AI classifier not loaded")
            return

        print("🔍 AI Analysis started...")

        try:
            if self.camera_timer:
                self.camera_timer.stop()

            res = self.classifier.predict(self.captured_frame)
            material = res['material']
            conf = res['confidence'] * 100

            print(f"✓ AI Result: {material} ({conf:.1f}%)")

            override = self.manual_material.currentText()
            manual = False
            if override != "Auto Detect":
                material = override
                conf = 100.0
                manual = True
                print(f"⚠ Manual override: {material}")

            settings = MATERIAL_SETTINGS.get(material, MATERIAL_SETTINGS['Clay'])

            # ==================== СОХРАНЕНИЕ ИЗОБРАЖЕНИЯ ====================

            # Создаём папку для артефактов если её нет
            artifacts_dir = "artifacts_photos"
            if not os.path.exists(artifacts_dir):
                os.makedirs(artifacts_dir)
                print(f"✓ Создана папка: {artifacts_dir}")

            # Генерируем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            photo_filename = f"{material}_{timestamp}.jpg"
            photo_path = os.path.join(artifacts_dir, photo_filename)

            # Сохраняем изображение
            cv2.imwrite(photo_path, self.captured_frame)
            print(f"✓ Изображение сохранено: {photo_path}")

            # ==================== ДОБАВЛЕНИЕ В БД ====================

            art_id = self.db.add_artifact(
                material=material,
                confidence=conf,
                container_id=self.selected_id,
                user_id=1,
                manual_override=manual,
                photo_path=photo_path,  # ← Добавляем путь к фото
                description=f"AI detected {material} with {conf:.1f}% confidence" + (
                    " (Manual override)" if manual else ""),
                location=f"Container #{self.selected_id}",
                archaeologist=self.main_window.current_user.get('full_name', 'Unknown') if hasattr(self.main_window,
                                                                                                   'current_user') else 'System'
            )

            print(f"✓ Artifact #{art_id} saved to database with photo")

            # Обновляем контейнер
            cont = self.containers[self.selected_id]
            cont['material'] = material
            cont['artifact_id'] = art_id
            cont['target_temp'] = settings['temp']
            cont['target_hum'] = settings['hum']

            # Отправляем настройки
            self.apply_settings(auto=True)

            # Обновляем UI
            self.update_material_table(material)
            self.update_recommendations(material)

            # Показываем результат с миниатюрой фото
            self.show_success_dialog(material, conf, art_id, photo_path)

            # Переходим на Overview
            self.tabs.setCurrentIndex(0)

            # Возобновляем камеру
            if self.camera:
                self.camera_timer.start(30)

        except Exception as e:
            print(f"✗ AI Analysis error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Analysis failed:\n{str(e)}")

    def show_success_dialog(self, material, confidence, artifact_id, photo_path):
        """Показать диалог успеха с миниатюрой фото"""
        try:
            msg = QMessageBox(self)
            msg.setWindowTitle("✓ Artifact Detected")
            msg.setIcon(QMessageBox.Information)

            # Текст
            text = f"<h2>✓ Artifact Successfully Classified!</h2>"
            text += f"<p><b>Material:</b> {material}</p>"
            text += f"<p><b>Confidence:</b> {confidence:.1f}%</p>"
            text += f"<p><b>Artifact ID:</b> #{artifact_id}</p>"
            text += f"<p><b>Photo saved:</b> {os.path.basename(photo_path)}</p>"
            text += f"<p style='color: green;'><i>Settings applied automatically to container.</i></p>"

            msg.setText(text)

            # Добавляем миниатюру фото
            if os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                if not pixmap.isNull():
                    # Масштабируем до 200x200
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    msg.setIconPixmap(scaled_pixmap)

            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        except Exception as e:
            print(f"⚠ Ошибка отображения диалога: {e}")
            # Fallback на простой диалог
            QMessageBox.information(self, "Success",
                                    f"✓ Artifact Detected!\n\nMaterial: {material}\nConfidence: {confidence:.1f}%\nID: #{artifact_id}\n\nPhoto saved: {photo_path}"
                                    )

    def closeEvent(self, event):
        if self.camera:
            self.camera.release()
        if self.data_fetcher:
            self.data_fetcher.stop()
            self.data_fetcher.wait()
        event.accept()
    def go_back(self):
        """Вернуться назад"""
        # Замени на правильный индекс страницы
        self.main_window.stacked_widget.setCurrentIndex(2)