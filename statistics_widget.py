from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random
from datetime import datetime, timedelta

class StatisticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # İstatistik kartları için frame
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout(stats_frame)
        
        # İstatistik kartları
        self.create_stat_card("Toplam Çalışma Süresi", "124 saat", "⏱️", stats_layout)
        self.create_stat_card("İşlenen Alan", "450 m²", "🌾", stats_layout)
        self.create_stat_card("Enerji Tüketimi", "85 kWh", "⚡", stats_layout)
        self.create_stat_card("Verimlilik", "%92", "📈", stats_layout)
        
        self.layout.addWidget(stats_frame)
        
        # Grafikler için container
        graphs_container = QFrame()
        graphs_container.setObjectName("graphsContainer")
        graphs_layout = QHBoxLayout(graphs_container)
        
        # Çalışma saatleri grafiği
        self.working_hours_chart = self.create_line_chart("Günlük Çalışma Saatleri")
        graphs_layout.addWidget(self.working_hours_chart)
        
        # Batarya kullanımı grafiği
        self.battery_usage_chart = self.create_line_chart("24 Saatlik Batarya Kullanımı (%)")
        graphs_layout.addWidget(self.battery_usage_chart)
        
        self.layout.addWidget(graphs_container)

    def create_stat_card(self, title, value, icon, parent_layout):
        card = QFrame()
        card.setProperty("class", "stat-card")
        layout = QVBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setProperty("class", "stat-icon")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setProperty("class", "stat-value")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "stat-title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        parent_layout.addWidget(card)

    def create_line_chart(self, title):
        fig = Figure(figsize=(6, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Test verileri
        hours = list(range(24))
        values = [random.randint(30, 100) for _ in range(24)]
        
        ax.plot(hours, values, color='#4ecca3', linewidth=2)
        ax.set_title(title, color='white', pad=20)
        ax.set_facecolor('#1a1a2e')
        fig.patch.set_facecolor('#16213e')
        
        # Eksenleri beyaz yap
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        fig.tight_layout()
        return canvas

    def update_translations(self, texts):
        """Metinleri güncelle"""
        pass  # İleride çeviri eklenecek 