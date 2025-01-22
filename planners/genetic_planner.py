from .base_planner import BasePlanner

class GeneticPlanner(BasePlanner):
    def __init__(self, grid_size):
        super().__init__(grid_size)
    
    def plan_path(self, start, goal, obstacles):
        print("Genetik algoritma planlayıcı henüz implement edilmedi")
        # Basit bir yol oluştur - köşegen
        path = []
        current = start
        while current != goal:
            path.append(current)
            dx = 1 if goal[0] > current[0] else -1 if goal[0] < current[0] else 0
            dy = 1 if goal[1] > current[1] else -1 if goal[1] < current[1] else 0
            current = (current[0] + dx, current[1] + dy)
        path.append(goal)
        return path 