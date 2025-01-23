from enum import Enum

class PlannerType(Enum):
    ADAPTIVE = "Adaptif Planlayıcı"
    ASTAR = "A* Algoritması"
    RRT = "RRT (Rapidly-exploring Random Trees)"
    POTENTIAL_FIELD = "Potansiyel Alan"
    VORONOI = "Voronoi Diyagramları"
    GENETIC = "Genetik Algoritma"
    ANT_COLONY = "Karınca Kolonisi"
    WAVEFRONT = "Dalga Yayılımı" 