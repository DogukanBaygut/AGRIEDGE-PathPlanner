from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QGridLayout, QProgressBar, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt

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
        
        # Sensör kartlarından sonra haritaları ekle
        maps_container = QFrame()
        maps_container.setObjectName("mapsContainer")
        maps_layout = QHBoxLayout(maps_container)
        maps_layout.setSpacing(20)

        # Sıcaklık haritası
        temp_frame = QFrame()
        temp_layout = QVBoxLayout(temp_frame)
        temp_title = QLabel("Sıcaklık Haritası")
        temp_title.setObjectName("mapTitle")
        temp_layout.addWidget(temp_title)
        
        self.temp_map = self.create_heat_map("temperature")
        temp_layout.addWidget(self.temp_map)
        maps_layout.addWidget(temp_frame)

        # Nem haritası
        humidity_frame = QFrame()
        humidity_layout = QVBoxLayout(humidity_frame)
        humidity_title = QLabel("Nem Haritası")
        humidity_title.setObjectName("mapTitle")
        humidity_layout.addWidget(humidity_title)
        
        self.humidity_map = self.create_heat_map("humidity")
        humidity_layout.addWidget(self.humidity_map)
        maps_layout.addWidget(humidity_frame)

        self.layout.addWidget(maps_container)

        # Haritalar için boyut politikası ekle
        maps_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        temp_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        humidity_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Test verileri için timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(2000)  # 2 saniyede bir güncelle
        
        # CSS stillerini ekle
        self.setStyleSheet("""
            QFrame#sensorCard {
                background-color: #16213e;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
                min-width: 200px;
            }
            QLabel {
                color: white;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #4ecca3;
                border-radius: 4px;
                text-align: center;
                background-color: #1a1a2e;
                color: white;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4ecca3;
                border-radius: 3px;
            }
            .sensor-icon {
                font-size: 24px;
                margin-right: 10px;
            }
            .sensor-title {
                font-weight: bold;
                color: #4ecca3;
            }
            QFrame#mapsContainer {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                min-height: 300px;
            }
            QLabel#mapTitle {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
                padding: 5px;
            }
        """)

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

    def create_heat_map(self, map_type):
        """Isı veya nem haritası oluştur"""
        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 30x30'luk örnek veri matrisi oluştur
        if map_type == "temperature":
            data = np.random.uniform(15, 35, (30, 30))  # 15-35°C arası
            cmap = 'RdYlBu_r'  # Kırmızı-Sarı-Mavi renk haritası
            title = "Sıcaklık Dağılımı (°C)"
        else:
            data = np.random.uniform(30, 90, (30, 30))  # %30-90 arası
            cmap = 'BuPu'  # Mavi-Mor renk haritası
            title = "Nem Dağılımı (%)"
        
        # Haritayı çiz
        im = ax.imshow(data, cmap=cmap, interpolation='nearest')
        cbar = fig.colorbar(im)
        
        # Colorbar yazı rengini ayarla
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')
        
        # Başlık ve eksen ayarları
        ax.set_title(title, color='white', pad=10, fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Arka plan rengini ayarla
        fig.patch.set_facecolor('#16213e')
        ax.set_facecolor('#1a1a2e')
        
        fig.tight_layout()
        return canvas

    def update_sensor_data(self):
        """Sensör verilerini ve haritaları güncelle"""
        self.soil_moisture.setValue(random.randint(30, 90))
        self.air_temp.setValue(random.randint(15, 35))
        self.humidity.setValue(random.randint(30, 90))
        self.light_level.setValue(random.randint(0, 100))
        
        # Haritaları güncelle
        try:
            # Sıcaklık haritası
            temp_fig = self.temp_map.figure
            temp_ax = temp_fig.axes[0]
            temp_data = np.random.uniform(15, 35, (30, 30))
            temp_ax.images[0].set_array(temp_data)
            
            # Colorbar değerlerini güncelle
            temp_ax.images[0].colorbar.update_normal(temp_ax.images[0])
            
            # Nem haritası
            humidity_fig = self.humidity_map.figure
            humidity_ax = humidity_fig.axes[0]
            humidity_data = np.random.uniform(30, 90, (30, 30))
            humidity_ax.images[0].set_array(humidity_data)
            
            # Colorbar değerlerini güncelle
            humidity_ax.images[0].colorbar.update_normal(humidity_ax.images[0])
            
            # Grafikleri yenile
            self.temp_map.draw()
            self.humidity_map.draw()
            
        except Exception as e:
            print(f"Harita güncelleme hatası: {e}") 