import sys
import os

# Modül yolunu ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Sonra importları yap
from widgets import StatisticsWidget, SensorWidget
from irrigation.widget import IrrigationWidget

import numpy as np
import heapq
import matplotlib.pyplot as plt
from planners.adaptive_planner import AdaptivePathPlanner
from matplotlib.colors import ListedColormap
import time
from mpl_toolkits.mplot3d import Axes3D  # 3D plotting için
from matplotlib import cm  # Renk haritaları için
import matplotlib.gridspec as gridspec  # Alt plotlar için
from path_planner_factory import PathPlannerFactory
from planners.planner_type import PlannerType
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QWidget, QLabel, QHBoxLayout, QFrame, QTabWidget,
    QProgressBar, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random  # Test verileri için

class FarmRobot:
    def __init__(self, grid_size=(10, 10)):
        self.grid_size = grid_size
        self.grid = np.zeros(grid_size)  # 0: boş, 1: işlenmiş, -1: engel
        self.position = (0, 0)
        self.path = []
        self.planner_factory = PathPlannerFactory()
        # Varsayılan olarak Adaptif planlayıcıyı seç
        self.current_planner = self.planner_factory.create_planner(PlannerType.ADAPTIVE, grid_size)
        self.current_algorithm = PlannerType.ADAPTIVE
        
    def set_planner(self, planner_type: PlannerType):
        """Yol planlama algoritmasını değiştir"""
        self.current_planner = self.planner_factory.create_planner(planner_type, self.grid_size)
        
    def set_obstacles(self, obstacles):
        """Tarlada engelleri ayarla (örn: ağaçlar, kayalar)"""
        for obs in obstacles:
            self.grid[obs] = -1
            
    def heuristic(self, a, b):
        """Manhattan mesafesi hesapla"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, pos):
        """Geçerli komşu pozisyonları bul"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4 yön: sağ, aşağı, sol, yukarı
            new_pos = (pos[0] + dx, pos[1] + dy)
            if (0 <= new_pos[0] < self.grid_size[0] and 
                0 <= new_pos[1] < self.grid_size[1] and 
                self.grid[new_pos] != -1):
                neighbors.append(new_pos)
        return neighbors
    
    def find_path(self, start, goal):
        """A* algoritması ile yol bulma"""
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # Yolu oluştur
        current = goal
        path = []
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        return path
    
    def plan_coverage_path(self):
        """Seçili algoritmaya göre yol planla"""
        if not self.current_planner:
            raise ValueError("Önce bir planlama algoritması seçilmeli!")
            
        obstacles = [(i, j) for i in range(self.grid_size[0]) 
                    for j in range(self.grid_size[1]) 
                    if self.grid[i, j] == -1]
                    
        self.path = self.current_planner.plan_path(
            self.position,
            (self.grid_size[0]-1, self.grid_size[1]-1),
            obstacles
        )
        return self.path
    
    def visualize(self):
        """Tarlayı ve robotu görselleştir"""
        plt.figure(figsize=(10, 10))
        
        # Özel renk haritası oluştur
        colors = ['#8B4513',  # Kahverengi (işlenmemiş toprak)
                 '#654321',   # Koyu kahverengi (işlenmiş toprak)
                 '#228B22']   # Yeşil (bitkiler/engeller)
        
        # Normalize edilmiş değerler için özel colormap
        custom_cmap = ListedColormap(colors)
        
        # Grid değerlerini 0,1,-1'den 0,1,2'ye dönüştür
        display_grid = self.grid.copy()
        display_grid[display_grid == -1] = 2  # Engelleri 2 yap
        
        plt.imshow(display_grid, cmap=custom_cmap)
        
        if self.path:
            path_y, path_x = zip(*self.path)
            
            # Ana yolu çiz
            plt.plot(path_x, path_y, 'white', linewidth=2, label='Robot Yolu')
            
            # Başlangıç noktasını göster
            plt.plot(self.position[1], self.position[0], 'ro', markersize=15, 
                    label='Başlangıç', markeredgecolor='white')
            
            # Bitiş noktasını göster
            plt.plot(path_x[-1], path_y[-1], 'bo', markersize=15, 
                    label='Bitiş', markeredgecolor='white')
            
            # Hareket yönünü gösteren okları ekle
            for i in range(len(path_x)-1):
                # Her 5 noktada bir ok göster
                if i % 5 == 0:
                    dx = path_x[i+1] - path_x[i]
                    dy = path_y[i+1] - path_y[i]
                    plt.arrow(path_x[i], path_y[i], dx*0.5, dy*0.5,
                            head_width=0.3, head_length=0.5, fc='yellow', ec='yellow')
        
        plt.grid(True, color='black', alpha=0.2)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.title('Tarım Robotu Simülasyonu')
        
        # Eksenleri etiketle
        plt.xlabel('X (metre)')
        plt.ylabel('Y (metre)')
        
        # Grafik düzenini ayarla
        plt.tight_layout()
        plt.show()

    def create_algorithm_dialog(self):
        """Algoritma seçim penceresi oluştur"""
        dialog = tk.Tk()
        dialog.title("Algoritma Seç")
        dialog.geometry("300x400")
        
        # Algoritma listesi
        algorithms_frame = ttk.Frame(dialog)
        algorithms_frame.pack(pady=20)
        
        algorithm_var = tk.StringVar(value=self.current_algorithm.value)
        
        for algorithm in PlannerType:
            ttk.Radiobutton(
                algorithms_frame,
                text=algorithm.value,
                value=algorithm.value,
                variable=algorithm_var
            ).pack(anchor='w', pady=5)
        
        def apply_selection():
            try:
                selected = algorithm_var.get()
                for alg in PlannerType:
                    if alg.value == selected:
                        print(f"Seçilen algoritma: {alg.value}")
                        self.current_algorithm = alg
                        self.set_planner(alg)
                        self.path = []  # Mevcut yolu temizle
                        self.plan_coverage_path()  # Yeni yol planla
                        if self.path:  # Yol başarıyla planlandıysa
                            dialog.destroy()
                            plt.close('all')  # Tüm figürleri kapat
                            self.simulate_movement(delay=0.1)  # Simülasyonu yeniden başlat
                        else:
                            print("Yol planlanamadı!")
                        break
            except Exception as e:
                print(f"Algoritma değiştirme hatası: {e}")
                dialog.destroy()
        
        # Uygula butonu
        ttk.Button(
            dialog,
            text="Uygula",
            command=apply_selection
        ).pack(pady=20)
        
        # İptal butonu
        ttk.Button(
            dialog,
            text="İptal",
            command=dialog.destroy
        ).pack(pady=5)
        
        dialog.mainloop()

    def simulate_movement(self, delay=0.05):
        """Robotun hareketini 2D ve 3D görünümle simüle et"""
        if not self.path:
            print("Önce bir yol planlanmalı!")
            return
        
        # Önceki figürleri temizle
        plt.close('all')
        
        # Figure ve subplot'ları ayarla
        fig = plt.figure(figsize=(20, 10))
        gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
        
        # Sabit subplot'ları oluştur
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], projection='3d')
        
        # Çıkış butonu ekle
        exit_ax = plt.axes([0.95, 0.01, 0.04, 0.03])
        exit_button = plt.Button(exit_ax, 'Çıkış', color='red', hovercolor='darkred')
        
        # Sonraki butonu ekle
        next_ax = plt.axes([0.90, 0.01, 0.04, 0.03])
        next_button = plt.Button(next_ax, 'Sonraki', color='green', hovercolor='darkgreen')
        
        # Algoritma seçim butonu ekle
        algo_ax = plt.axes([0.85, 0.01, 0.04, 0.03])
        algo_button = plt.Button(algo_ax, 'Algoritma', color='blue', hovercolor='darkblue')
        
        # Simülasyon kontrol değişkenleri
        self.simulation_finished = False
        self.next_simulation = False
        
        def exit_simulation(event):
            plt.close('all')
            self.simulation_finished = True
            
        def next_simulation(event):
            plt.close('all')
            self.next_simulation = True
            
        def change_algorithm(event):
            self.create_algorithm_dialog()
        
        exit_button.on_clicked(exit_simulation)
        next_button.on_clicked(next_simulation)
        algo_button.on_clicked(change_algorithm)
        
        # Başlangıç görünüm açısı
        elev = 30
        azim = 45
        
        try:
            # Her adımı görselleştir
            for i, new_pos in enumerate(self.path):
                if not plt.get_fignums():
                    break
                    
                # Subplot'ları temizle
                ax1.clear()
                ax2.clear()
                
                # Mevcut görünüm açısını al
                if hasattr(ax2, 'elev') and hasattr(ax2, 'azim'):
                    elev = ax2.elev
                    azim = ax2.azim
                
                # 2D ve 3D görünümleri çiz
                self._plot_2d(ax1, i, new_pos)
                self._plot_3d(ax2, i, new_pos, elev, azim)
                
                # Görünümü güncelle
                plt.tight_layout()
                plt.draw()
                plt.pause(delay)
            
            if plt.get_fignums():
                plt.show()
            
        except Exception as e:
            print(f"Görselleştirme hatası: {e}")
            
        finally:
            plt.close(fig)
    
    def _plot_2d(self, ax, step_index, current_pos):
        """2D görünümü çiz"""
        # Robotun pozisyonunu güncelle
        self.position = current_pos
        self.grid[current_pos] = 1
        
        # Özel renk haritası
        colors = ['#8B4513',  # Kahverengi (işlenmemiş toprak)
                 '#654321',   # Koyu kahverengi (işlenmiş toprak)
                 '#228B22']   # Yeşil (bitkiler/engeller)
        custom_cmap = ListedColormap(colors)
        
        # Grid'i göster
        display_grid = self.grid.copy()
        display_grid[display_grid == -1] = 2
        ax.imshow(display_grid, cmap=custom_cmap)
        
        # Yolları çiz
        if self.path and len(self.path) > 0:
            path_y, path_x = zip(*self.path)
            # Tüm yolu soluk göster
            ax.plot(path_x, path_y, 'white', alpha=0.3, linewidth=2, label='Planlanan Yol')
            
            # Gidilen yolu göster
            if step_index > 0:
                current_path_y, current_path_x = zip(*self.path[:step_index+1])
                ax.plot(current_path_x, current_path_y, 'yellow', linewidth=3, label='Gidilen Yol')
            
            # Robot ve hedef konumunu göster
            ax.plot(self.position[1], self.position[0], 'ro', markersize=15, 
                    label='Robot', markeredgecolor='white')
            ax.plot(path_x[-1], path_y[-1], 'bo', markersize=15, 
                    label='Hedef', markeredgecolor='white')
        
        ax.grid(True, color='black', alpha=0.2)
        ax.set_title(f'AgriEDGE Tarla Simülasyonu\n2D Görünüm - Adım {step_index+1}/{len(self.path) if self.path else 0}')
        ax.set_xlabel('X (metre)')
        ax.set_ylabel('Y (metre)')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    def _plot_3d(self, ax, step_index, current_pos, elev=30, azim=45):
        """3D görünümü daha estetik bir şekilde göster"""
        # Grid verilerini 3D yüzeye dönüştür
        X, Y = np.meshgrid(range(self.grid_size[1]), range(self.grid_size[0]))
        Z = np.zeros_like(self.grid, dtype=float)
        
        # Orijinal grid'i kopyala (işlenmiş alanları göz ardı et)
        display_grid = self.grid.copy()
        display_grid[display_grid == 1] = 0  # İşlenmiş alanları normal toprak olarak göster
        
        # Yükseklikleri sadeleştir
        base_height = 0.0  # Temel yükseklik
        Z[display_grid == 0] = base_height  # Tüm toprak aynı seviyede
        Z[display_grid == -1] = base_height + 0.02  # Engeller hafif yüksek
        
        # Özel renk haritası
        colors = ['#C19A6B',  # Açık kahve (toprak)
                 '#C19A6B',  # Aynı renk (işlenmiş toprak için)
                 '#228B22']   # Yeşil (engeller)
        custom_cmap = ListedColormap(colors)
        
        # Zemini çiz
        surf = ax.plot_surface(X, Y, Z, cmap=custom_cmap,
                             rstride=1, cstride=1,
                             linewidth=0, antialiased=True,
                             alpha=1.0)
        
        # Robot ve yol yüksekliği - zeminden biraz yukarıda
        path_height = base_height + 0.04  # Yol yüksekliği
        robot_height = path_height  # Robot yolu ile aynı yükseklikte
        
        # Yolu çiz
        if self.path and len(self.path) > 0:
            path_y, path_x = zip(*self.path)
            
            # Ana yolu çiz
            path_z = [path_height] * len(self.path)
            ax.plot(path_x, path_y, path_z, color='white', 
                   alpha=0.7, linewidth=3, label='Planlanan Yol')
            
            # Gidilen yolu göster
            if step_index > 0:
                current_path_y, current_path_x = zip(*self.path[:step_index+1])
                current_path_z = [path_height] * (step_index + 1)
                ax.plot(current_path_x, current_path_y, current_path_z, 
                       color='#FFD700', linewidth=4, label='Gidilen Yol')
            
            # Robot ve hedefi göster
            ax.scatter([current_pos[1]], [current_pos[0]], [robot_height],
                      color='red', s=200, label='Robot',
                      edgecolor='white', linewidth=2)
            
            ax.scatter([path_x[-1]], [path_y[-1]], [robot_height],
                      color='blue', s=200, label='Hedef',
                      edgecolor='white', linewidth=2)
        
        # Görünüm ayarları
        ax.view_init(elev=elev, azim=azim)
        ax.set_box_aspect([1, 1, 0.3])
        
        # Eksen ayarları
        ax.set_title('AgriEDGE Tarla Simülasyonu\n3D Arazi Görünümü',
                    pad=20, fontsize=12)
        
        # Eksenleri ve kenar çizgilerini gizle
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        
        # Kenar çizgilerini gizle
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        ax.xaxis.pane.set_edgecolor('none')
        ax.yaxis.pane.set_edgecolor('none')
        ax.zaxis.pane.set_edgecolor('none')
        
        # Arka plan rengini ayarla
        ax.set_facecolor('#F0F8FF')
        
        # Sınırları ayarla - z ekseni aralığını daralt
        margin = 2
        ax.set_xlim(-margin, self.grid_size[1] + margin)
        ax.set_ylim(-margin, self.grid_size[0] + margin)
        ax.set_zlim(base_height - 0.05, base_height + 0.08)

class FarmRobotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgriEDGE Robot Kontrol Merkezi")
        self.setGeometry(100, 100, 1200, 800)
        self.is_connected = False
        self.current_task = None

        # Metin çevirileri
        self.translations = {
            "tr": {
                "title": "AgriEDGE",
                "subtitle": "Akıllı Tarım Kontrol Sistemi",
                "connect": "Robota Bağlan",
                "disconnect": "Bağlantıyı Kes",
                "start": "Simülasyonu Başlat",
                "exit": "Çıkış",
                "task_selection": "Görev Seçimi",
                "mapping": "Haritalama",
                "hoeing": "Çapalama",
                "current_task": "Mevcut Görev",
                "no_task": "Görev Yok",
                "waiting": "Bağlantı Bekleniyor",
                "connected": "Robot Bağlandı",
                "stats": "İstatistikler",
                "sensors": "Sensörler",
                "stats_title": "İstatistikler",
                "sensors_title": "Sensörler",
                "working_hours": "Günlük Çalışma Saatleri",
                "battery_usage": "24 Saatlik Batarya Kullanımı (%)",
                "total_work_time": "Toplam Çalışma Süresi",
                "processed_area": "İşlenen Alan",
                "energy_consumption": "Enerji Tüketimi",
                "efficiency": "Verimlilik",
                "soil_moisture": "Toprak Nemi",
                "air_temp": "Hava Sıcaklığı",
                "humidity": "Nem Oranı",
                "light_level": "Işık Seviyesi",
                "hours": "saat",
                "camera_view": "Kamera Görüntüsü Bekleniyor...",
                "temp_map": "Sıcaklık Haritası",
                "humidity_map": "Nem Haritası",
                "irrigation_prediction": "Sulama Tahmini",
                "irrigation_priority": "Sulama Önceliği",
                "reasons": "Nedenler",
                "no_irrigation_needed": "Sulama gerekmiyor"
            },
            "en": {
                "title": "AgriEDGE",
                "subtitle": "Smart Agriculture Control System",
                "connect": "Connect to Robot",
                "disconnect": "Disconnect",
                "start": "Start Simulation",
                "exit": "Exit",
                "task_selection": "Task Selection",
                "mapping": "Mapping",
                "hoeing": "Hoeing",
                "current_task": "Current Task",
                "no_task": "No Task",
                "waiting": "Waiting for Connection",
                "connected": "Robot Connected",
                "stats": "Statistics",
                "sensors": "Sensors",
                "stats_title": "Statistics",
                "sensors_title": "Sensors",
                "working_hours": "Daily Working Hours",
                "battery_usage": "24-Hour Battery Usage (%)",
                "total_work_time": "Total Work Time",
                "processed_area": "Processed Area",
                "energy_consumption": "Energy Consumption",
                "efficiency": "Efficiency",
                "soil_moisture": "Soil Moisture",
                "air_temp": "Air Temperature",
                "humidity": "Humidity",
                "light_level": "Light Level",
                "hours": "hours",
                "camera_view": "Waiting for Camera Feed...",
                "temp_map": "Temperature Map",
                "humidity_map": "Humidity Map",
                "irrigation_prediction": "Irrigation Prediction",
                "irrigation_priority": "Irrigation Priority",
                "reasons": "Reasons",
                "no_irrigation_needed": "No irrigation needed"
            }
        }

        # Tema stilleri - Ortak buton stillerini koru
        self.button_styles = """
            QPushButton#primaryButton { 
                background-color: #4ecca3; 
                color: #1a1a2e;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton#primaryButton:hover { 
                background-color: #45b592; 
            }
            QPushButton#dangerButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton#dangerButton:hover {
                background-color: #c0392b;
            }
            QPushButton#taskButton {
                background-color: transparent;
                border: 1px solid #4ecca3;
                color: #4ecca3;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton#taskButton:hover:enabled {
                background-color: rgba(78, 204, 163, 0.1);
            }
            QPushButton#taskButton:checked {
                background-color: #4ecca3;
                color: #1a1a2e;
            }
            QPushButton#taskButton:disabled {
                background-color: transparent;
                border: 1px solid #2d2d44;
                color: #2d2d44;
            }
        """

        self.themes = {
            "dark": f"""
                QMainWindow {{ background-color: #1a1a2e; }}
                QFrame {{ border: none; }}
                QLabel {{ color: white; }}  /* Tüm labellar için beyaz renk */
                
                #headerPanel, #controlPanel {{ 
                    background-color: #16213e;
                    border-radius: 10px;
                }}
                #mainTitle {{ 
                    color: #4ecca3;
                    font-size: 24px;
                    font-weight: bold;
                }}
                #subtitle {{ 
                    color: #a2a2a2;
                    font-size: 13px;
                }}
                #connectionStatus {{ 
                    color: #a2a2a2;
                    font-size: 13px;
                    padding: 5px 15px;
                    background: rgba(78, 204, 163, 0.1);
                    border-radius: 15px;
                }}
                #sectionHeader {{ 
                    color: #4ecca3;
                    font-size: 16px;
                    font-weight: bold;
                }}
                #taskStatus {{ 
                    color: #a2a2a2;
                    font-size: 13px;
                }}
                #mapTitle {{
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    margin: 5px;
                }}
                #mapsContainer {{
                    background-color: #16213e;
                    border-radius: 10px;
                    padding: 15px;
                }}
                .sensor-title {{
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                }}
                .sensor-value {{
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                }}
                .sensor-unit {{
                    color: #a2a2a2;
                    font-size: 12px;
                }}
                #sensorCard {{
                    background-color: #16213e;
                    border-radius: 8px;
                    padding: 10px;
                }}
                {self.button_styles}
            """,
            "light": f"""
                QMainWindow {{ background-color: #f0f0f0; }}
                QFrame {{ border: none; }}
                #headerPanel, #controlPanel {{ 
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                #mainTitle {{ 
                    color: #4ecca3;
                    font-size: 24px;
                    font-weight: bold;
                }}
                #subtitle {{ 
                    color: #555555;
                    font-size: 13px;
                }}
                #connectionStatus {{ 
                    color: #555555;
                    font-size: 13px;
                    padding: 5px 15px;
                    background: rgba(78, 204, 163, 0.1);
                    border-radius: 15px;
                }}
                #sectionHeader {{ 
                    color: #4ecca3;
                    font-size: 16px;
                    font-weight: bold;
                }}
                #taskStatus {{ 
                    color: #555555;
                    font-size: 13px;
                }}
                #mapTitle {{
                    color: #555555;
                    font-size: 14px;
                    font-weight: bold;
                    margin: 5px;
                }}
                #mapsContainer {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 15px;
                }}
                .sensor-title {{
                    color: #555555;
                    font-size: 13px;
                    font-weight: bold;
                }}
                .sensor-value {{
                    color: #555555;
                    font-size: 20px;
                    font-weight: bold;
                }}
                .sensor-unit {{
                    color: #555555;
                    font-size: 12px;
                }}
                #sensorCard {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 10px;
                }}
                {self.button_styles}
            """
        }

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Üst panel
        header_panel = QFrame()
        header_panel.setObjectName("headerPanel")
        header_layout = QHBoxLayout(header_panel)  # Önce header_layout'u tanımla
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Dil ve tema ayarları için başlangıç değerleri
        self.current_language = "tr"  # Varsayılan dil
        self.is_dark_mode = True      # Varsayılan tema
        
        # Ayarlar butonu ve menüsü
        settings_container = QFrame()
        settings_layout = QHBoxLayout(settings_container)
        settings_layout.setSpacing(10)
        
        # Tema değiştirme butonu
        self.theme_button = self.create_button("🌙", "iconButton")
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        # Dil değiştirme butonu
        self.language_button = self.create_button("🇹🇷", "iconButton")
        self.language_button.setFixedSize(40, 40)
        self.language_button.clicked.connect(self.toggle_language)
        
        settings_layout.addWidget(self.theme_button)
        settings_layout.addWidget(self.language_button)
        header_layout.addWidget(settings_container, alignment=Qt.AlignRight)

        # Logo ve başlık
        logo_title = QFrame()
        logo_layout = QVBoxLayout(logo_title)
        logo_layout.setSpacing(5)
        
        title = QLabel("AgriEDGE")
        title.setObjectName("mainTitle")
        subtitle = QLabel("Akıllı Tarım Kontrol Sistemi")
        subtitle.setObjectName("subtitle")
        
        logo_layout.addWidget(title)
        logo_layout.addWidget(subtitle)
        header_layout.addWidget(logo_title)

        # Bağlantı durumu
        self.connection_status = QLabel("⭘ Bağlantı Bekleniyor")
        self.connection_status.setObjectName("connectionStatus")
        header_layout.addWidget(self.connection_status, alignment=Qt.AlignRight)

        main_layout.addWidget(header_panel)

        # Kontrol paneli
        control_panel = QFrame()
        control_panel.setObjectName("controlPanel")
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(20)

        # Sol kontrol grubu
        left_controls = QFrame()
        left_layout = QVBoxLayout(left_controls)
        left_layout.setSpacing(15)

        # Ana kontrol butonları
        self.connect_button = self.create_button("Robota Bağlan", "primaryButton")
        start_button = self.create_button("Simülasyonu Başlat", "primaryButton")
        exit_button = self.create_button("Çıkış", "dangerButton")

        left_layout.addWidget(self.connect_button)
        left_layout.addWidget(start_button)
        left_layout.addWidget(exit_button)
        left_layout.addStretch()

        # Sağ kontrol grubu - Görev seçimi
        right_controls = QFrame()
        right_controls.setObjectName("taskPanel")
        right_layout = QVBoxLayout(right_controls)
        right_layout.setSpacing(15)

        task_header = QLabel("Görev Seçimi")
        task_header.setObjectName("sectionHeader")
        right_layout.addWidget(task_header)

        # Görev butonları
        task_buttons = QVBoxLayout()
        task_buttons.setSpacing(10)
        
        self.mapping_button = self.create_button("Haritalama", "taskButton")
        self.hoeing_button = self.create_button("Çapalama", "taskButton")
        
        self.mapping_button.setCheckable(True)
        self.hoeing_button.setCheckable(True)
        self.mapping_button.setEnabled(False)
        self.hoeing_button.setEnabled(False)
        
        task_buttons.addWidget(self.mapping_button)
        task_buttons.addWidget(self.hoeing_button)
        right_layout.addLayout(task_buttons)

        # Mevcut görev durumu
        self.current_task_label = QLabel("Mevcut Görev: Yok")
        self.current_task_label.setObjectName("taskStatus")
        right_layout.addWidget(self.current_task_label)
        right_layout.addStretch()

        # Panelleri ana layout'a ekle
        control_layout.addWidget(left_controls, 1)
        control_layout.addWidget(right_controls, 1)
        main_layout.addWidget(control_panel)

        # Kontrol panelinden sonra tab widget ekle
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabs")
        main_layout.addWidget(self.tab_widget)

        # İstatistik ve sensör sekmelerini ekle
        stats_widget = StatisticsWidget()
        sensor_widget = SensorWidget()
        
        self.tab_widget.addTab(stats_widget, "İstatistikler")
        self.tab_widget.addTab(sensor_widget, "Sensörler")

        # Sulama widget'ını ekle
        irrigation_widget = IrrigationWidget()
        self.tab_widget.addTab(irrigation_widget, "Sulama Tahmini")

        # Tab widget stilini ekle
        self.setStyleSheet("""
            QTabWidget::pane {
                background-color: #16213e;
                border: none;
                border-radius: 10px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #1a1a2e;
                color: #a2a2a2;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #16213e;
                color: #4ecca3;
            }
            QTabBar::tab:hover {
                background-color: #1e2642;
            }
            
            /* İstatistik kartları için stiller */
            QFrame#statsFrame, QFrame#graphsContainer {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
            }
            QFrame.stat-card {
                background-color: #1a1a2e;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QLabel.stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #4ecca3;
            }
            QLabel.stat-title {
                font-size: 14px;
                color: #a2a2a2;
            }
            QLabel.stat-icon {
                font-size: 28px;
            }
            
            /* Sensör kartları için stiller */
            QFrame#sensorCard {
                background-color: #16213e;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QProgressBar {
                border: 1px solid #4ecca3;
                border-radius: 4px;
                text-align: center;
                background-color: #1a1a2e;
                color: #a2a2a2;
            }
            QProgressBar::chunk {
                background-color: #4ecca3;
                border-radius: 3px;
            }
        """)

        # Buton bağlantıları
        self.connect_button.clicked.connect(self.toggle_connection)
        start_button.clicked.connect(self.start_simulation)
        exit_button.clicked.connect(self.close)
        self.mapping_button.clicked.connect(lambda: self.set_task("Haritalama"))
        self.hoeing_button.clicked.connect(lambda: self.set_task("Çapalama"))

        # Ana stilleri ekle
        self.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #4ecca3;
                color: #1a1a2e;
            }
            QPushButton#primaryButton:hover {
                background-color: #45b592;
            }
            QPushButton#dangerButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#dangerButton:hover {
                background-color: #c0392b;
            }
            QPushButton#taskButton {
                background-color: #1a1a2e;
                border: 1px solid #4ecca3;
                color: #4ecca3;
            }
            QPushButton#taskButton:hover:enabled {
                background-color: rgba(78, 204, 163, 0.1);
            }
            QPushButton#taskButton:checked {
                background-color: #4ecca3;
                color: #1a1a2e;
            }
            QPushButton#taskButton:disabled {
                background-color: #1a1a2e;
                border: 1px solid #2d2d44;
                color: #2d2d44;
            }
        """ + self.styleSheet())

    def create_button(self, text, object_name):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def set_task(self, task_name):
        """Görevi ayarla ve diğer butonu temizle"""
        if task_name == "Haritalama":
            self.hoeing_button.setChecked(False)
            if self.mapping_button.isChecked():
                self.current_task = "Haritalama"
            else:
                self.current_task = None
        else:
            self.mapping_button.setChecked(False)
            if self.hoeing_button.isChecked():
                self.current_task = "Çapalama"
            else:
                self.current_task = None
                
        # Mevcut görev etiketini güncelle
        if self.current_task:
            self.current_task_label.setText(f"Mevcut Görev: {self.current_task}")
            self.current_task_label.setStyleSheet("color: #7DD181; font-size: 12px;")
        else:
            self.current_task_label.setText("Mevcut Görev: Yok")
            self.current_task_label.setStyleSheet("color: #95A5A6; font-size: 12px;")

    def toggle_connection(self):
        """Robot bağlantısını aç/kapat"""
        self.is_connected = not self.is_connected
        if self.is_connected:
            self.connection_status.setText("🟢 Robot Bağlandı")
            self.connection_status.setStyleSheet("""
                font-size: 13px; 
                color: #2ECC71;
                padding: 3px;
                margin: 0px;
            """)
            self.connect_button.setText("Bağlantıyı Kes")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2ecc71, stop:1 #27ae60);
                    border: none;
                    color: white;
                    padding: 10px 20px;                        /* Daha küçük padding */
                    font-size: 12px;                           /* Daha küçük yazı */
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #27ae60, stop:1 #219a52);
                }
                QPushButton:pressed {
                    padding: 9px 19px;                         /* Basıldığında küçülme efekti */
                }
            """)
            # Bağlantı varsa görev butonlarını aktif et
            self.mapping_button.setEnabled(True)
            self.hoeing_button.setEnabled(True)
        else:
            self.connection_status.setText("⭘ Bağlantı Bekleniyor")
            self.connection_status.setStyleSheet("""
                font-size: 13px; 
                color: #95A5A6;
                padding: 3px;
                margin: 0px;
            """)
            self.connect_button.setText("Robota Bağlan")
            self.connect_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2ecc71, stop:1 #27ae60);
                    border: none;
                    color: white;
                    padding: 10px 20px;                        /* Daha küçük padding */
                    font-size: 12px;                           /* Daha küçük yazı */
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #27ae60, stop:1 #219a52);
                }
                QPushButton:pressed {
                    padding: 9px 19px;                         /* Basıldığında küçülme efekti */
                }
            """)
            # Bağlantı yoksa görev butonlarını deaktif et
            self.mapping_button.setEnabled(False)
            self.hoeing_button.setEnabled(False)
            # Görev seçimini sıfırla
            self.current_task = None
            self.mapping_button.setChecked(False)
            self.hoeing_button.setChecked(False)
            self.current_task_label.setText("Mevcut Görev: Yok")
            self.current_task_label.setStyleSheet("color: #95A5A6; font-size: 12px;")

    def start_simulation(self):
        # Tarla konfigürasyonları
        grid_size = (30, 30)
        field_configs = [
            # Tarla 1: Dikey engeller
            [
                *[(i, 5) for i in range(1, 25)],  # Uzun dikey engel
                *[(i, 15) for i in range(1, 25)], # İkinci dikey engel
                *[(i, 25) for i in range(1, 25)], # Üçüncü dikey engel
            ],
            # Tarla 2: Yatay engeller
            [
                *[(5, j) for j in range(1, 25)],  # Uzun yatay engel
                *[(15, j) for j in range(1, 25)], # İkinci yatay engel
                *[(25, j) for j in range(1, 25)], # Üçüncü yatay engel
            ],
            # Tarla 3: Karma desenler
            [
                # Büyük L şeklinde engeller
                *[(5, j) for j in range(5, 15)],
                *[(i, 5) for i in range(5, 15)],
                *[(15, j) for j in range(15, 25)],
                *[(i, 15) for i in range(15, 25)],
            ],
            # Tarla 4: Çapraz engeller
            [
                *[(i, i) for i in range(1, 25)],  # Çapraz engel
                *[(i, 25-i) for i in range(1, 25)],  # Ters çapraz engel
            ]
        ]

        i = 0
        while i < len(field_configs):
            print(f"\nTarla {i+1} simülasyonu başlıyor...")
            
            # Yeni robot oluştur
            robot = FarmRobot(grid_size)
            
            # Başlangıçta bir planlama algoritması seç
            robot.set_planner(PlannerType.ADAPTIVE)
            
            # Engelleri ayarla
            robot.set_obstacles(field_configs[i])
            
            # Yol planla
            start_time = time.time()
            robot.plan_coverage_path()
            planning_time = time.time() - start_time
            
            print(f"Yol planlama süresi: {planning_time:.2f} saniye")
            print(f"Toplam adım sayısı: {len(robot.path)}")
            
            # Hareketi simüle et
            robot.simulate_movement(delay=0.1)
            
            # Simülasyon kontrolü
            if robot.simulation_finished:
                break
            elif robot.next_simulation:
                i += 1
            else:
                i += 1

    def toggle_theme(self):
        """Tema değiştirme"""
        self.is_dark_mode = not self.is_dark_mode
        self.theme_button.setText("🌙" if self.is_dark_mode else "☀️")
        self.apply_theme()

    def toggle_language(self):
        """Dil değiştirme"""
        self.current_language = "en" if self.current_language == "tr" else "tr"
        self.language_button.setText("🇹🇷" if self.current_language == "tr" else "🇬🇧")
        self.update_texts()

    def apply_theme(self):
        """Temayı uygula"""
        theme = self.themes["dark"] if self.is_dark_mode else self.themes["light"]
        self.setStyleSheet(theme)

    def update_texts(self):
        """Tüm metinleri güncelle"""
        texts = self.translations[self.current_language]
        
        # Başlık ve alt başlık
        self.findChild(QLabel, "mainTitle").setText(texts["title"])
        self.findChild(QLabel, "subtitle").setText(texts["subtitle"])
        
        # Butonlar
        self.connect_button.setText(texts["connect"])
        self.findChild(QPushButton, "primaryButton").setText(texts["start"])
        self.findChild(QPushButton, "dangerButton").setText(texts["exit"])
        
        # Görev butonları
        self.mapping_button.setText(texts["mapping"])
        self.hoeing_button.setText(texts["hoeing"])
        
        # Durum metinleri
        self.findChild(QLabel, "sectionHeader").setText(texts["task_selection"])
        
        # Görev durumu metnini güncelle
        if self.current_task:
            # Türkçe görev adlarını İngilizce karşılıklarıyla eşle
            task_translations = {
                "Haritalama": "mapping",
                "Çapalama": "hoeing"
            }
            # Görev adını çevir
            task_key = task_translations.get(self.current_task, "")
            if task_key:
                self.current_task_label.setText(f"{texts['current_task']}: {texts[task_key]}")
            else:
                self.current_task_label.setText(f"{texts['current_task']}: {texts['no_task']}")
        else:
            self.current_task_label.setText(f"{texts['current_task']}: {texts['no_task']}")
        
        # Bağlantı durumu
        if self.is_connected:
            self.connection_status.setText(f"🟢 {texts['connected']}")
        else:
            self.connection_status.setText(f"⭘ {texts['waiting']}")
        
        # Sekmeler
        self.tab_widget.setTabText(0, texts["stats"])
        self.tab_widget.setTabText(1, texts["sensors"])

        # İstatistik widget'ını güncelle
        stats_widget = self.findChild(StatisticsWidget)
        if stats_widget:
            stats_widget.update_translations(texts)

        # Sensör widget'ını güncelle
        sensor_widget = self.findChild(SensorWidget)
        if sensor_widget:
            sensor_widget.update_translations(texts)

# Test kısmını güncelle
if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')  # Modern görünüm için Fusion stilini kullan
    window = FarmRobotGUI()
    window.show()
    app.exec_() 