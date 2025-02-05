from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QGridLayout
from PyQt5.QtCore import QTimer, Qt
from .data_generator import WeatherDataGenerator
from .predictor import IrrigationPredictor

class IrrigationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data_generator = WeatherDataGenerator()
        self.predictor = IrrigationPredictor()
        self.setup_ui()
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_predictions)
        self.timer.start(5000)  # 5 saniyede bir güncelle
        
        # CSS stillerini ekle
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
            }
            
            QLabel#sectionHeader {
                color: #4ecca3;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                margin-bottom: 10px;
            }
            
            QFrame#irrigationStatus {
                background-color: #16213e;
                border-radius: 12px;
                padding: 20px;
                margin: 10px;
                border: 1px solid rgba(78, 204, 163, 0.2);
            }
            
            QFrame#sensorValues {
                background-color: #16213e;
                border-radius: 12px;
                padding: 20px;
                margin: 10px;
                border: 1px solid rgba(78, 204, 163, 0.2);
            }
            
            QLabel {
                color: white;
                font-size: 14px;
            }
            
            QLabel#urgencyLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            
            QLabel#reasonsLabel {
                color: #a2a2a2;
                font-size: 14px;
                padding: 10px;
                background-color: rgba(26, 26, 46, 0.5);
                border-radius: 8px;
            }
            
            QLabel[urgency="Düşük"] {
                color: #2ecc71;
                border: 2px solid #2ecc71;
                background-color: rgba(46, 204, 113, 0.1);
            }
            
            QLabel[urgency="Orta"] {
                color: #f1c40f;
                border: 2px solid #f1c40f;
                background-color: rgba(241, 196, 15, 0.1);
            }
            
            QLabel[urgency="Yüksek"] {
                color: #e74c3c;
                border: 2px solid #e74c3c;
                background-color: rgba(231, 76, 60, 0.1);
            }
            
            /* Sensör değerleri için özel stiller */
            QLabel[type="value"] {
                color: #4ecca3;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 15px;
                background-color: rgba(78, 204, 163, 0.1);
                border-radius: 6px;
                min-width: 80px;
            }
            
            QLabel[type="label"] {
                font-size: 14px;
                color: #a2a2a2;
            }
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("Sulama Tahmini")
        title.setObjectName("sectionHeader")
        layout.addWidget(title)
        
        # Durum göstergesi
        self.status_frame = QFrame()
        self.status_frame.setObjectName("irrigationStatus")
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setSpacing(10)
        
        self.urgency_label = QLabel("Sulama Önceliği: -")
        self.urgency_label.setObjectName("urgencyLabel")
        self.urgency_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.urgency_label)
        
        self.reasons_label = QLabel("Nedenler: -")
        self.reasons_label.setObjectName("reasonsLabel")
        status_layout.addWidget(self.reasons_label)
        
        layout.addWidget(self.status_frame)
        
        # Sensör değerleri
        values_frame = QFrame()
        values_frame.setObjectName("sensorValues")
        values_layout = QGridLayout(values_frame)
        values_layout.setSpacing(15)
        
        # Etiketler ve değerler
        labels = ["Toprak Nemi:", "Sıcaklık:", "Nem:"]
        self.values = [QLabel("-") for _ in range(3)]
        
        for i, (label, value) in enumerate(zip(labels, self.values)):
            label_widget = QLabel(label)
            label_widget.setProperty("type", "label")
            value.setProperty("type", "value")
            value.setAlignment(Qt.AlignCenter)
            
            values_layout.addWidget(label_widget, i, 0)
            values_layout.addWidget(value, i, 1)
        
        self.soil_moisture_value = self.values[0]
        self.temperature_value = self.values[1]
        self.humidity_value = self.values[2]
        
        layout.addWidget(values_frame)

    def update_predictions(self):
        # Simüle edilmiş güncel veri al
        current_data = self.data_generator.generate_current_data()
        
        # Değerleri güncelle
        self.soil_moisture_value.setText(f"{current_data['soil_moisture']:.1f}%")
        self.temperature_value.setText(f"{current_data['temperature']:.1f}°C")
        self.humidity_value.setText(f"{current_data['humidity']:.1f}%")
        
        # Tahmin al
        prediction = self.predictor.predict_irrigation_time(current_data)
        
        # UI güncelle
        self.urgency_label.setText(f"Sulama Önceliği: {prediction['urgency']}")
        self.urgency_label.setProperty("urgency", prediction['urgency'])
        self.urgency_label.style().unpolish(self.urgency_label)
        self.urgency_label.style().polish(self.urgency_label)
        
        if prediction['reasons']:
            self.reasons_label.setText("Nedenler: " + ", ".join(prediction['reasons']))
        else:
            self.reasons_label.setText("Nedenler: Sulama gerekmiyor") 