from .base_planner import BasePlanner

class VoronoiPlanner(BasePlanner):
    def __init__(self, grid_size):
        super().__init__(grid_size)
    
    def plan_path(self, start, goal, obstacles):
        print("Voronoi planlayıcı henüz implement edilmedi")
        # Basit bir yol döndür
        return [start, goal] 