import numpy as np
from .base_planner import BasePlanner

class RRTPlanner(BasePlanner):
    def __init__(self, grid_size):
        super().__init__(grid_size)
        self.step_size = 1
        self.max_iterations = 10000
        
    def plan_path(self, start, goal, obstacles):
        self.nodes = [start]
        self.parents = {start: None}
        
        for _ in range(self.max_iterations):
            # Rastgele nokta seç
            if np.random.random() < 0.1:
                random_point = goal
            else:
                random_point = (
                    np.random.randint(0, self.grid_size[0]),
                    np.random.randint(0, self.grid_size[1])
                )
            
            # En yakın düğümü bul
            nearest_node = self._find_nearest(random_point)
            
            # Yeni düğüm oluştur
            new_node = self._steer(nearest_node, random_point)
            
            # Engel kontrolü
            if new_node not in obstacles and self._is_path_clear(nearest_node, new_node, obstacles):
                self.nodes.append(new_node)
                self.parents[new_node] = nearest_node
                
                # Hedefe ulaştık mı?
                if self._distance(new_node, goal) < self.step_size:
                    path = self._reconstruct_path(new_node)
                    path.append(goal)
                    return path
        
        return None
    
    def _find_nearest(self, point):
        distances = [self._distance(point, node) for node in self.nodes]
        return self.nodes[np.argmin(distances)]
    
    def _steer(self, from_point, to_point):
        dx = to_point[0] - from_point[0]
        dy = to_point[1] - from_point[1]
        dist = self._distance(from_point, to_point)
        
        if dist <= self.step_size:
            return to_point
        
        theta = np.arctan2(dy, dx)
        return (
            int(from_point[0] + self.step_size * np.cos(theta)),
            int(from_point[1] + self.step_size * np.sin(theta))
        )
    
    def _distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def _is_path_clear(self, p1, p2, obstacles):
        # Basit çizgi kontrolü
        points = self._interpolate(p1, p2)
        return not any(point in obstacles for point in points)
    
    def _interpolate(self, p1, p2):
        points = []
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        steps = max(abs(dx), abs(dy))
        
        if steps == 0:
            return [p1]
            
        x_step = dx / steps
        y_step = dy / steps
        
        for i in range(steps + 1):
            x = int(p1[0] + i * x_step)
            y = int(p1[1] + i * y_step)
            points.append((x, y))
            
        return points
    
    def _reconstruct_path(self, node):
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = self.parents[current]
        return path[::-1]
    
    def extend_tree(self, random_point):
        # Ağacı genişletme
        pass 