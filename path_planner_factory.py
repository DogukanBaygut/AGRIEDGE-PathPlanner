from planners.planner_type import PlannerType
from planners.rrt_planner import RRTPlanner
from planners.potential_field_planner import PotentialFieldPlanner
from planners.adaptive_planner import AdaptivePathPlanner
from planners.astar_planner import AStarPlanner
from planners.voronoi_planner import VoronoiPlanner
from planners.genetic_planner import GeneticPlanner
from planners.ant_colony_planner import AntColonyPlanner
from planners.wavefront_planner import WavefrontPlanner

class PathPlannerFactory:
    @staticmethod
    def create_planner(planner_type: PlannerType, grid_size):
        if planner_type == PlannerType.ADAPTIVE:
            return AdaptivePathPlanner(grid_size)
        elif planner_type == PlannerType.ASTAR:
            return AStarPlanner(grid_size)
        elif planner_type == PlannerType.RRT:
            return RRTPlanner(grid_size)
        elif planner_type == PlannerType.POTENTIAL_FIELD:
            return PotentialFieldPlanner(grid_size)
        elif planner_type == PlannerType.VORONOI:
            return VoronoiPlanner(grid_size)
        elif planner_type == PlannerType.GENETIC:
            return GeneticPlanner(grid_size)
        elif planner_type == PlannerType.ANT_COLONY:
            return AntColonyPlanner(grid_size)
        elif planner_type == PlannerType.WAVEFRONT:
            return WavefrontPlanner(grid_size)
        else:
            # Varsayılan olarak Adaptif planlayıcıyı döndür
            print(f"Uyarı: {planner_type.value} henüz implement edilmedi. Adaptif planlayıcı kullanılıyor.")
            return AdaptivePathPlanner(grid_size) 