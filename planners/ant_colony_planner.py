from .base_planner import BasePlanner

class AntColonyPlanner(BasePlanner):
    def __init__(self, grid_size):
        super().__init__(grid_size)
    
    def plan_path(self, start, goal, obstacles):
        print("Karınca kolonisi planlayıcı henüz implement edilmedi")
        # Basit bir yol oluştur - önce x sonra y
        path = []
        current = start
        # Önce x koordinatını ayarla
        while current[0] != goal[0]:
            path.append(current)
            dx = 1 if goal[0] > current[0] else -1
            current = (current[0] + dx, current[1])
        # Sonra y koordinatını ayarla
        while current[1] != goal[1]:
            path.append(current)
            dy = 1 if goal[1] > current[1] else -1
            current = (current[0], current[1] + dy)
        path.append(goal)
        return path 