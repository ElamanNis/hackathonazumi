"""
ИИ-классификатор для Teachable Machine (TensorFlow 2.15)
"""

import cv2
import numpy as np
from PIL import Image
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
    print(f"✓ TensorFlow {tf.__version__} загружен")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("✗ TensorFlow не установлен")

class ArtifactClassifier:
    def __init__(self, model_path="keras_model.h5",
                 labels_path="labels1.txt"):

        self.model = None
        self.class_names = []
        self.input_shape = (224, 224)
        self.confidence_threshold = 0.60

        if not TENSORFLOW_AVAILABLE:
            print("✗ TensorFlow не доступен")
            return

        # Проверка файлов
        if not os.path.exists(model_path):
            print(f"✗ Модель не найдена: {model_path}")
            print(f"   Текущая директория: {os.getcwd()}")
            return

        if not os.path.exists(labels_path):
            print(f"✗ Файл меток не найден: {labels_path}")
            return

        try:
            print(f"🔄 Загрузка модели: {model_path}")

            # Простая загрузка (работает в TensorFlow 2.15)
            self.model = keras.models.load_model(model_path, compile=False)

            print(f"✓ Модель загружена успешно!")

            # Загрузка меток
            with open(labels_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.class_names = []
                for line in lines:
                    line = line.strip()
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) == 2 and parts[0].isdigit():
                            self.class_names.append(parts[1])
                        else:
                            self.class_names.append(line)

            if len(self.class_names) == 0:
                print(f"✗ Не удалось загрузить классы")
                self.model = None
                return

            print(f"✓ Классы загружены ({len(self.class_names)}): {self.class_names}")
            print(f"✓ ИИ классификатор готов к работе!")

        except Exception as e:
            print(f"✗ Ошибка загрузки модели: {e}")
            import traceback
            traceback.print_exc()
            self.model = None

    def preprocess_image(self, image):
        """
        Предобработка изображения
        """
        try:
            # OpenCV BGR → RGB
            if isinstance(image, np.ndarray):
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)

            # Resize 224x224
            image = image.resize(self.input_shape, Image.LANCZOS)

            # Numpy array
            image_array = np.asarray(image, dtype=np.float32)

            # Нормализация: (pixel / 127.5) - 1
            normalized_image = (image_array / 127.5) - 1.0

            # Batch dimension
            input_data = np.expand_dims(normalized_image, axis=0)

            return input_data

        except Exception as e:
            print(f"✗ Ошибка предобработки: {e}")
            return None

    def predict(self, image):
        """
        Классификация изображения
        """
        if self.model is None:
            print("⚠ Модель не загружена")
            return {
                'material': 'Unknown (Model not loaded)',
                'confidence': 0.0,
                'all_predictions': [],
                'is_confident': False
            }

        try:
            # Предобработка
            input_data = self.preprocess_image(image)
            if input_data is None:
                raise Exception("Предобработка не удалась")

            print("🔄 Запуск ИИ анализа...")

            # Предсказание
            predictions = self.model.predict(input_data, verbose=0)[0]

            print(f"✓ Анализ завершён. Shape: {predictions.shape}")

            # Формирование результатов
            all_predictions = []
            for i in range(min(len(self.class_names), len(predictions))):
                class_name = self.class_names[i]
                confidence = float(predictions[i])
                all_predictions.append((class_name, confidence))
                print(f"   {class_name}: {confidence*100:.1f}%")

            all_predictions.sort(key=lambda x: x[1], reverse=True)

            # Лучший результат
            best_class = all_predictions[0][0]
            best_confidence = all_predictions[0][1]
            is_confident = best_confidence >= self.confidence_threshold

            print(f"✓ Результат: {best_class} ({best_confidence*100:.1f}%)")
            print(f"   Уверенность {'✓ ВЫСОКАЯ' if is_confident else '⚠ низкая'}")

            return {
                'material': best_class,
                'confidence': best_confidence,
                'all_predictions': all_predictions,
                'is_confident': is_confident
            }

        except Exception as e:
            print(f"✗ Ошибка предсказания: {e}")
            import traceback
            traceback.print_exc()
            return {
                'material': 'Error during prediction',
                'confidence': 0.0,
                'all_predictions': [],
                'is_confident': False
            }

    def get_conservation_settings(self, material):
        """
        Рекомендации по консервации
        """
        settings_map = {
            'metal': {'temperature': 5.0, 'humidity': 12.0, 'spray': 'BTA (Benzotriazole)', 'description': 'Low humidity to prevent corrosion'},
            'bronze': {'temperature': 5.0, 'humidity': 12.0, 'spray': 'BTA (Benzotriazole)', 'description': 'Bronze disease prevention'},
            'iron': {'temperature': 5.0, 'humidity': 10.0, 'spray': 'None', 'description': 'Very low humidity for iron'},
            'ceramic': {'temperature': 20.0, 'humidity': 50.0, 'spray': 'Water', 'description': 'Moderate conditions for ceramics'},
            'pottery': {'temperature': 20.0, 'humidity': 50.0, 'spray': 'Water', 'description': 'Stable humidity for pottery'},
            'bone': {'temperature': 18.0, 'humidity': 55.0, 'spray': 'Water', 'description': 'Moderate humidity for organic materials'},
            'wood': {'temperature': 18.0, 'humidity': 55.0, 'spray': 'Water', 'description': 'Prevent drying and cracking'},
            'organic': {'temperature': 18.0, 'humidity': 55.0, 'spray': 'Alcohol', 'description': 'Prevent biological growth'},
            'stone': {'temperature': 20.0, 'humidity': 45.0, 'spray': 'None', 'description': 'Stable conditions for stone'},
            'glass': {'temperature': 20.0, 'humidity': 42.0, 'spray': 'None', 'description': 'Prevent weeping glass syndrome'},
        }

        material_lower = material.lower()
        for key, settings in settings_map.items():
            if key in material_lower:
                return settings

        print(f"⚠ Нет настроек для '{material}', используем по умолчанию")
        return {
            'temperature': 20.0,
            'humidity': 50.0,
            'spray': 'None',
            'description': 'Default preservation settings'
        }
