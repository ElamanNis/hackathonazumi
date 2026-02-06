"""
Управление базой данных SQLite - Полная версия
"""

import sqlite3
import hashlib
from datetime import datetime
import os


class Database:
    def __init__(self, db_path="artifacts.db"):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = db_path
        self.init_database()
        self.migrate_database()  # ← Добавь эту строку

    def init_database(self):
        """Инициализация таблиц базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'archaeologist',
                created_at TEXT,
                last_login TEXT
            )
        """)

        # Таблица артефактов (ОБНОВЛЁННАЯ с новыми полями)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_path TEXT,
                material TEXT,
                confidence REAL,
                manual_override INTEGER DEFAULT 0,
                location TEXT,
                description TEXT,
                depth REAL,
                date_found TEXT,
                time_found TEXT,
                archaeologist TEXT,
                project TEXT,
                container_id INTEGER,
                container_mode TEXT,
                latitude REAL,
                longitude REAL,
                user_id INTEGER,
                added_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()
        print("✓ База данных инициализирована")

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, full_name=""):
        """Регистрация нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, full_name, created_at))

            conn.commit()
            conn.close()
            return True, "Регистрация успешна"
        except sqlite3.IntegrityError:
            return False, "Пользователь с таким именем уже существует"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def login_user(self, username, password):
        """Вход пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            password_hash = self.hash_password(password)

            cursor.execute("""
                SELECT id, username, full_name, role FROM users
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))

            user = cursor.fetchone()

            if user:
                # Обновляем время последнего входа
                last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    UPDATE users SET last_login = ? WHERE id = ?
                """, (last_login, user[0]))
                conn.commit()

                conn.close()
                return True, {
                    "id": user[0],
                    "username": user[1],
                    "full_name": user[2],
                    "role": user[3]
                }
            else:
                conn.close()
                return False, "Неверное имя пользователя или пароль"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    # ==================== НОВЫЙ МЕТОД ====================
    def migrate_database(self):
        """Миграция базы данных - добавление недостающих колонок"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Проверяем существующие колонки
            cursor.execute("PRAGMA table_info(artifacts)")
            columns = [col[1] for col in cursor.fetchall()]

            # Добавляем недостающие колонки
            if 'manual_override' not in columns:
                cursor.execute("ALTER TABLE artifacts ADD COLUMN manual_override INTEGER DEFAULT 0")
                print("✓ Добавлена колонка manual_override")

            if 'container_id' not in columns:
                cursor.execute("ALTER TABLE artifacts ADD COLUMN container_id INTEGER")
                print("✓ Добавлена колонка container_id")

            if 'added_at' not in columns:
                cursor.execute("ALTER TABLE artifacts ADD COLUMN added_at TEXT")
                print("✓ Добавлена колонка added_at")

            conn.commit()
            conn.close()
            print("✓ Миграция базы данных завершена")

        except Exception as e:
            print(f"✗ Ошибка миграции: {e}")

    def add_artifact(self, material, confidence, container_id, user_id=None, manual_override=False, **kwargs):
        """
        Добавление артефакта в базу данных

        Args:
            material (str): Материал артефакта (Clay, Glass, Iron, etc.)
            confidence (float): Уверенность AI (0-100)
            container_id (int): ID контейнера
            user_id (int): ID пользователя
            manual_override (bool): True если археолог исправил AI
            **kwargs: Дополнительные поля (location, depth, description, photo_path, etc.)

        Returns:
            int: ID добавленного артефакта
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_found = kwargs.get('date_found', datetime.now().strftime("%Y-%m-%d"))
            time_found = kwargs.get('time_found', datetime.now().strftime("%H:%M:%S"))

            cursor.execute("""
                INSERT INTO artifacts 
                (material, confidence, manual_override, container_id, user_id, added_at, 
                 date_found, time_found, location, depth, description, photo_path, 
                 archaeologist, project, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                material,
                confidence,
                1 if manual_override else 0,  # SQLite использует INTEGER для BOOLEAN
                container_id,
                user_id,
                added_at,
                date_found,
                time_found,
                kwargs.get('location', 'Container Scan'),
                kwargs.get('depth', 0.0),
                kwargs.get('description', f'AI detected {material} with {confidence:.1f}% confidence'),
                kwargs.get('photo_path', ''),
                kwargs.get('archaeologist', 'AI System'),
                kwargs.get('project', 'FLL UNEARTHED'),
                kwargs.get('latitude', 0.0),
                kwargs.get('longitude', 0.0)
            ))

            conn.commit()
            artifact_id = cursor.lastrowid
            conn.close()

            print(f"✓ Артефакт #{artifact_id} добавлен в БД (Материал: {material}, Confidence: {confidence:.1f}%)")
            return artifact_id

        except Exception as e:
            print(f"✗ Ошибка добавления артефакта: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_artifact(self, artifact_id):
        """Получение информации об артефакте"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, material, confidence, manual_override, date_found, 
                       container_id, location, description
                FROM artifacts WHERE id = ?
            """, (artifact_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'material': row[1],
                    'confidence': row[2],
                    'manual_override': bool(row[3]),
                    'date_found': row[4],
                    'container_id': row[5],
                    'location': row[6],
                    'description': row[7]
                }
            return None

        except Exception as e:
            print(f"✗ Ошибка получения артефакта: {e}")
            return None

    def get_all_artifacts(self):
        """Получение всех артефактов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, material, confidence, manual_override, date_found, container_id
                FROM artifacts ORDER BY added_at DESC
            """)

            rows = cursor.fetchall()
            conn.close()

            artifacts = []
            for row in rows:
                artifacts.append({
                    'id': row[0],
                    'material': row[1],
                    'confidence': row[2],
                    'manual_override': bool(row[3]),
                    'date_found': row[4],
                    'container_id': row[5]
                })

            return artifacts

        except Exception as e:
            print(f"✗ Ошибка получения артефактов: {e}")
            return []

    def update_artifact(self, artifact_id, **kwargs):
        """Обновление данных артефакта"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Формируем SQL динамически
            fields = []
            values = []

            for key, value in kwargs.items():
                if key in ['material', 'confidence', 'manual_override', 'location', 'description',
                          'depth', 'photo_path', 'archaeologist', 'project']:
                    fields.append(f"{key} = ?")
                    values.append(value)

            if not fields:
                return False

            values.append(artifact_id)
            sql = f"UPDATE artifacts SET {', '.join(fields)} WHERE id = ?"

            cursor.execute(sql, values)
            conn.commit()
            conn.close()

            print(f"✓ Артефакт #{artifact_id} обновлён")
            return True

        except Exception as e:
            print(f"✗ Ошибка обновления артефакта: {e}")
            return False

    def delete_artifact(self, artifact_id):
        """Удаление артефакта"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM artifacts WHERE id = ?", (artifact_id,))

            conn.commit()
            conn.close()

            print(f"✓ Артефакт #{artifact_id} удалён")
            return True

        except Exception as e:
            print(f"✗ Ошибка удаления артефакта: {e}")
            return False
