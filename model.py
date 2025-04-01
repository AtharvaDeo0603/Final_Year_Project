import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os
import pandas as pd
from PIL import Image

class EWasteClassifier:
    def __init__(self):
        self.IMG_SIZE = 50
        self.NUM_CLASSES = 6  # Updated class count
        self.CLASSES = ['Batteries', 'Mobile & PCBs', 'Peripherals', 'Printers & Screens', 'Large Appliances']
        
        self.CREDIT_POINTS = {
            'Batteries': 20,
            'Mobile & PCBs': 30,
            'Peripherals': 15,
            'Printers & Screens': 25,
            'Large Appliances': 40,
            'Mixed Electronics': 10
        }
        
        self.MODEL_PATH = 'ewaste_classifier.h5'
        self.model = None
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.create_directories()
        
        # Load component database
        self.component_data = pd.read_csv("ewaste_components.csv") if os.path.exists("ewaste_components.csv") else None

    def create_directories(self):
        """Ensure the dataset folders exist"""
        directories = [
            'train/Batteries', 'train/Mobile & PCBs', 'train/Peripherals',
            'train/Printers & Screens', 'train/Large Appliances',
            'val/Batteries', 'val/Mobile & PCBs', 'val/Peripherals',
            'val/Printers & Screens', 'val/Large Appliances'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.data_dir, directory), exist_ok=True)

    def check_data_availability(self, data_dir):
        """Check if dataset contains images"""
        missing_classes = []
        for class_name in self.CLASSES:
            class_path = os.path.join(data_dir, class_name)
            if not os.path.exists(class_path) or len(os.listdir(class_path)) == 0:
                missing_classes.append(class_name)
        
        if missing_classes:
            raise ValueError(f"Missing or empty directories: {', '.join(missing_classes)}")

    def load_and_preprocess_data(self, data_dir):
        """Load and process images for training"""
        self.check_data_availability(os.path.join(self.data_dir, data_dir))

        images, labels = [], []
        
        for class_idx, class_name in enumerate(self.CLASSES):
            class_path = os.path.join(self.data_dir, data_dir, class_name)
            for img_name in os.listdir(class_path):
                img_path = os.path.join(class_path, img_name)
                try:
                    img = Image.open(img_path)
                    img = img.resize((self.IMG_SIZE, self.IMG_SIZE))
                    img_array = np.array(img) / 255.0
                    images.append(img_array)
                    labels.append(class_idx)
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")

        return np.array(images), np.array(labels)

    def create_model(self):
        """Define CNN model"""
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.IMG_SIZE, self.IMG_SIZE, 3)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.NUM_CLASSES, activation='softmax')
        ])
        
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model

    def train(self):
        """Train the model"""
        print("Starting training...")

        X_train, y_train = self.load_and_preprocess_data('train')
        X_val, y_val = self.load_and_preprocess_data('val')

        self.model = self.create_model()
        history = self.model.fit(X_train, y_train, epochs=20, validation_data=(X_val, y_val), batch_size=32)

        self.model.save(self.MODEL_PATH)
        print("✅ Model trained and saved!")

    def load_model(self):
        """Load saved model"""
        if os.path.exists(self.MODEL_PATH):
            self.model = tf.keras.models.load_model(self.MODEL_PATH)
            return True
        return False

    def predict(self, image):
        """Make a prediction and return valuable components"""
        if self.model is None:
            if not self.load_model():
                raise ValueError("❌ Model not found. Train the model first!")

        img = Image.open(image)
        img = img.resize((self.IMG_SIZE, self.IMG_SIZE))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = self.model.predict(img_array)
        predicted_class = self.CLASSES[np.argmax(prediction)]
        confidence = float(np.max(prediction))
        points = self.CREDIT_POINTS[predicted_class]
        
        # Retrieve valuable components from the dataset
        if self.component_data is not None:
            device_info = self.component_data[self.component_data["Device Type"] == predicted_class]
            if not device_info.empty:
                components = device_info["Components Present"].values[0]
                estimated_value = device_info["Estimated Value (₹)"].values[0]
            else:
                components = "Unknown"
                estimated_value = "N/A"
        else:
            components = "Unknown"
            estimated_value = "N/A"

        return {
            'class': predicted_class,
            'confidence': confidence,
            'points': points,
            'components': components,
            'estimated_value': estimated_value
        }

if __name__ == "__main__":
    classifier = EWasteClassifier()
    classifier.train()
