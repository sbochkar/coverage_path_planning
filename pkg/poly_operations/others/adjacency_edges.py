"""Module for computing adjacency between edges in a dict."""
from typing import Dict, Tuple
from shapely.geometry import Polygon


def get_neighbor_map(polygon: Polygon) -> Dict[Tuple[float, float], Tuple[Tuple[float, float]]]:
    """This function will form an adjacency list representing polygon's edges.

    Args:
        polygon (Polygon): Shapely object representing the polygon.

    Returns:
        neighbors_map (Dict): A map between vertex and its two neighbors.
    """
    neighbors_map: Dict[Tuple[float, float], Tuple[Tuple[float, float]]] = {}
    for chain in [polygon.exterior, *polygon.interiors]:
        for idx, coord in list(enumerate(chain.coords))[:-1]:
            neighbors_map[coord] = (chain.coords[idx - (1 if idx != 0 else 2)],
                                    chain.coords[idx + 1])
    return neighbors_map
