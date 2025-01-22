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

# Test edelim
if __name__ == "__main__":
    # Daha büyük tarla boyutu (30x30)
    grid_size = (30, 30)
    
    # Farklı tarla konfigürasyonları
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
        robot.set_planner(PlannerType.ADAPTIVE)  # Varsayılan olarak Adaptif planlayıcıyı kullan
        
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