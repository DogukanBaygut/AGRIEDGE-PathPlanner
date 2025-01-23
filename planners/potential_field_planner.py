from .base_planner import BasePlanner
import numpy as np

class PotentialFieldPlanner(BasePlanner):
    def __init__(self, grid_size):
        super().__init__(grid_size)
        
    def plan_path(self, start, goal, obstacles):
        print("Potansiyel Alan planlayıcı henüz implement edilmedi")
        # Basit bir yol oluştur - düz çizgi
        path = [start]
        current = start
        while current != goal:
            dx = np.sign(goal[0] - current[0])
            dy = np.sign(goal[1] - current[1])
            if dx != 0:
                current = (current[0] + dx, current[1])
            elif dy != 0:
                current = (current[0], current[1] + dy)
            path.append(current)
        return path
    
    def calculate_potential(self, point, goal, obstacles):
        # Potansiyel hesaplama
        pass 