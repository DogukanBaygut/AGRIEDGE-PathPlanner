import numpy as np
import pickle
import os
from collections import defaultdict

class AdaptivePathPlanner:
    def __init__(self, grid_size):
        """Adaptif yol planlayıcı başlatma"""
        self.grid_size = grid_size
        # Başarılı rotaları saklamak için hafıza
        self.path_memory = defaultdict(list)
        # Rota başarı metriklerini tutmak için sözlük
        self.path_scores = defaultdict(float)
        # Hata durumlarını kaydetmek için log
        self.error_log = defaultdict(list)
        # Öğrenme oranı
        self.learning_rate = 0.1
        # Hafıza dosya yolu
        self.memory_file = 'path_memory.pkl'
        
        # Eğer varsa önceki hafızayı yükle
        self._load_memory()
    
    def _load_memory(self):
        """Önceki çalışmalardan kaydedilmiş hafızayı yükle"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    saved_data = pickle.load(f)
                    self.path_memory = saved_data.get('memory', self.path_memory)
                    self.path_scores = saved_data.get('scores', self.path_scores)
            except Exception as e:
                print(f"Hafıza yükleme hatası: {e}")
    
    def save_memory(self):
        """Mevcut hafızayı kaydet"""
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump({
                    'memory': self.path_memory,
                    'scores': self.path_scores
                }, f)
        except Exception as e:
            print(f"Hafıza kaydetme hatası: {e}")
    
    def plan_path(self, start, goal, obstacles):
        """Yol planla"""
        key = self._get_path_key(obstacles)
        
        # Hafızada benzer durum var mı kontrol et
        if key in self.path_memory and self.path_scores[key] > 0.7:
            # Başarılı rotalardan en iyisini seç
            best_path = max(self.path_memory[key], 
                          key=lambda p: self._evaluate_path(p, obstacles))
            return self._adapt_path(best_path, start, goal, obstacles)
        
        # Hafızada uygun yol yoksa, basit bir kapsama yolu oluştur
        complete_path = []
        current_pos = start
        direction = 1  # 1: aşağı, -1: yukarı
        
        # Her sütunu dikey olarak tara
        for x in range(self.grid_size[1]):
            if direction == 1:  # Aşağı doğru
                y_range = range(self.grid_size[0])
            else:  # Yukarı doğru
                y_range = range(self.grid_size[0] - 1, -1, -1)
                
            for y in y_range:
                target = (y, x)
                if target not in obstacles:  # Engel değilse
                    if target != current_pos:
                        # A* ile alt yolları bul
                        sub_path = self._find_path(current_pos, target, obstacles)
                        if sub_path:
                            complete_path.extend(sub_path[1:])  # İlk pozisyonu atlayarak ekle
                    current_pos = target
            
            # Bir sonraki sütuna geç
            if x < self.grid_size[1] - 1:
                next_x = x + 1
                direction *= -1  # Yön değiştir
                
                # Bir sonraki sütunun başlangıç noktasını belirle
                if direction == 1:
                    next_target = (0, next_x)  # Üst
                else:
                    next_target = (self.grid_size[0]-1, next_x)  # Alt
                
                if next_target not in obstacles:
                    sub_path = self._find_path(current_pos, next_target, obstacles)
                    if sub_path:
                        complete_path.extend(sub_path[1:])
                    current_pos = next_target
        
        # Yeni yolu öğren
        self.learn_from_path(complete_path, 1.0, obstacles)
        return complete_path
    
    def learn_from_path(self, path, success_score, obstacles):
        """Tamamlanan bir rotadan öğren"""
        key = self._get_path_key(obstacles)
        self.path_memory[key].append(path)
        
        # Başarı puanını güncelle
        current_score = self.path_scores[key]
        self.path_scores[key] = (1 - self.learning_rate) * current_score + self.learning_rate * success_score
        
        # Hafızayı kaydet
        self.save_memory()
    
    def _get_path_key(self, obstacles):
        """Engel konfigürasyonuna göre benzersiz anahtar oluştur"""
        return hash(tuple(sorted(obstacles)))
    
    def _evaluate_path(self, path, obstacles):
        """Rotayı değerlendir"""
        if not path:
            return 0.0
            
        # Rota uzunluğu
        length_score = 1.0 / len(path)
        
        # Engellerden uzaklık
        clearance_score = self._calculate_clearance(path, obstacles)
        
        # Dönüş sayısı
        turn_score = self._calculate_turn_score(path)
        
        return 0.4 * length_score + 0.4 * clearance_score + 0.2 * turn_score
    
    def _calculate_clearance(self, path, obstacles):
        """Rotanın engellerden ortalama uzaklığını hesapla"""
        if not obstacles:
            return 1.0
            
        total_clearance = 0
        for pos in path:
            min_dist = min(abs(pos[0] - obs[0]) + abs(pos[1] - obs[1]) 
                         for obs in obstacles)
            total_clearance += min_dist
            
        return total_clearance / len(path)
    
    def _calculate_turn_score(self, path):
        """Rotadaki dönüş sayısına göre skor hesapla"""
        if len(path) < 3:
            return 1.0
            
        turns = 0
        for i in range(1, len(path)-1):
            dx1 = path[i][0] - path[i-1][0]
            dy1 = path[i][1] - path[i-1][1]
            dx2 = path[i+1][0] - path[i][0]
            dy2 = path[i+1][1] - path[i][1]
            
            if (dx1, dy1) != (dx2, dy2):
                turns += 1
                
        return 1.0 / (turns + 1)
    
    def _adapt_path(self, path, start, goal, obstacles):
        """Mevcut duruma göre rotayı adapte et"""
        if not path:
            return None
            
        # Başlangıç ve bitiş noktalarını ayarla
        adapted_path = self._adjust_endpoints(path, start, goal)
        
        # Engellere göre rotayı düzelt
        adapted_path = self._avoid_obstacles(adapted_path, obstacles)
        
        return adapted_path
    
    def _adjust_endpoints(self, path, start, goal):
        """Rotanın başlangıç ve bitiş noktalarını ayarla"""
        path = list(path)
        path[0] = start
        path[-1] = goal
        return path
    
    def _avoid_obstacles(self, path, obstacles):
        """Engellere çarpmayacak şekilde rotayı düzelt"""
        safe_path = []
        for pos in path:
            if pos not in obstacles:
                safe_path.append(pos)
            else:
                # En yakın güvenli noktayı bul
                safe_pos = self._find_safe_position(pos, obstacles)
                safe_path.append(safe_pos)
        return safe_path
    
    def _find_safe_position(self, pos, obstacles):
        """Verilen konuma en yakın güvenli pozisyonu bul"""
        directions = [(0,1), (1,0), (0,-1), (-1,0)]
        for d in directions:
            new_pos = (pos[0] + d[0], pos[1] + d[1])
            if (0 <= new_pos[0] < self.grid_size[0] and 
                0 <= new_pos[1] < self.grid_size[1] and 
                new_pos not in obstacles):
                return new_pos
        return pos 
    
    def _find_path(self, start, goal, obstacles):
        """A* algoritması ile iki nokta arasında yol bul"""
        if start == goal:
            return [start]
            
        # Manhattan mesafesi için heuristik
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # Komşu noktaları bul
        def get_neighbors(pos):
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if (0 <= new_pos[0] < self.grid_size[0] and 
                    0 <= new_pos[1] < self.grid_size[1] and 
                    new_pos not in obstacles):
                    neighbors.append(new_pos)
            return neighbors
        
        # A* algoritması
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = frontier.pop(0)[1]
            
            if current == goal:
                break
                
            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    frontier.append((priority, next_pos))
                    frontier.sort()  # Önceliğe göre sırala
                    came_from[next_pos] = current
        
        # Yolu oluştur
        if goal not in came_from:
            return None
            
        current = goal
        path = []
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path 