from abc import ABC, abstractmethod

class BasePlanner(ABC):
    def __init__(self, grid_size):
        self.grid_size = grid_size
    
    @abstractmethod
    def plan_path(self, start, goal, obstacles):
        """Yol planlama metodu - her alt sınıf implement etmeli"""
        pass 