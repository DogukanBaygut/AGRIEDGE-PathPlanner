from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, 
    QGridLayout, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
import random

class SensorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Sensör kartları için grid layout
        sensor_grid = QGridLayout()
        sensor_grid.setSpacing(10)
        
        # Sensör değerleri için progress bar'lar
        self.soil_moisture = QProgressBar()
        self.air_temp = QProgressBar()
        self.humidity = QProgressBar()
        self.light_level = QProgressBar()
        
        # Progress bar'ların maksimum değerlerini ayarla
        self.soil_moisture.setMaximum(100)
        self.air_temp.setMaximum(50)  # Maksimum 50°C
        self.humidity.setMaximum(100)
        self.light_level.setMaximum(100)
        
        # Sensör kartlarını oluştur
        self.create_sensor_card("Toprak Nemi", "💧", self.soil_moisture, "%", sensor_grid, 0, 0)
        self.create_sensor_card("Hava Sıcaklığı", "🌡️", self.air_temp, "°C", sensor_grid, 0, 1)
        self.create_sensor_card("Nem Oranı", "💨", self.humidity, "%", sensor_grid, 0, 2)
        self.create_sensor_card("Işık Seviyesi", "☀️", self.light_level, "lux", sensor_grid, 0, 3)
        
        sensor_frame = QFrame()
        sensor_frame.setLayout(sensor_grid)
        self.layout.addWidget(sensor_frame)
        
        # Test verileri için timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(2000)  # 2 saniyede bir güncelle

    def create_sensor_card(self, title, icon, value_widget, unit, parent_layout, row, col):
        card = QFrame()
        card.setObjectName("sensorCard")
        layout = QVBoxLayout(card)
        
        # İkon ve başlık
        header = QFrame()
        header_layout = QHBoxLayout(header)
        
        icon_label = QLabel(icon)
        title_label = QLabel(title)
        title_label.setObjectName(title.lower().replace(" ", "_"))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        layout.addWidget(header)
        
        # Değer widget'ı
        if isinstance(value_widget, QProgressBar):
            value_widget.setFixedHeight(25)
            value_widget.setTextVisible(True)
            value_widget.setFormat(f"{unit}%v")
        
        layout.addWidget(value_widget)
        parent_layout.addWidget(card, row, col)

    def update_sensor_data(self):
        """Sensör verilerini güncelle"""
        self.soil_moisture.setValue(random.randint(30, 90))
        self.air_temp.setValue(random.randint(15, 35))
        self.humidity.setValue(random.randint(30, 90))
        self.light_level.setValue(random.randint(0, 100))

    def update_translations(self, texts):
        """Metinleri güncelle"""
        pass  # İleride çeviri eklenecek 