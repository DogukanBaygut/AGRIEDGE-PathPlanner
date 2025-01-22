from .base_planner import BasePlanner
import heapq

class AStarPlanner(BasePlanner):
    def __init__(self, grid_size):
        super().__init__(grid_size)
    
    def plan_path(self, start, goal, obstacles):
        """A* algoritması ile yol planla"""
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_pos in self._get_neighbors(current, obstacles):
                new_cost = cost_so_far[current] + 1
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self._heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # Yolu oluştur
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        return path
    
    def _heuristic(self, a, b):
        """Manhattan mesafesi hesapla"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _get_neighbors(self, pos, obstacles):
        """Geçerli komşu pozisyonları bul"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_pos = (pos[0] + dx, pos[1] + dy)
            if (0 <= new_pos[0] < self.grid_size[0] and 
                0 <= new_pos[1] < self.grid_size[1] and 
                new_pos not in obstacles):
                neighbors.append(new_pos)
        return neighbors 