"""Interface layer with visilibity library."""
from typing import List, Optional

from shapely.geometry import LinearRing, Point, Polygon
from visilibity import Point as VisPoint, Polygon as VisPolygon, Environment, Visibility_Polygon

from log_utils import get_logger


# pylint: disable=invalid-name
logger = get_logger("visible_polygon")
# pylint: enable=invalid-name


EPSILON = 0.00001


def compute_vis_polygon(polygon: Polygon, vertex: Point) -> Optional[Polygon]:
    """Compute visible subset of polygon from vertex.

    TODO: Confirm and ensure that the CCW/CW directions of exterior/interiors are true.

    Args:
        polygon (Polygon): Shapely object representing the polygon.
        vertex (Point): Shapely object representing the vertex.

    Returns:
        visible_polygon (Polygon): Shapely object representing visible polygon.
    """
    observer = VisPoint(vertex.x, vertex.y)

    vis_polygons: List[VisPolygon] = []
    for chain in [polygon.exterior, *polygon.interiors]:
        vis_polygons.append(VisPolygon([VisPoint(*point) for point in chain.coords[:-1]]))

    vis_environment = Environment(vis_polygons)
    if not vis_environment.is_valid(EPSILON):
        logger.error("Error when creating Visilibity environment.")
        return None

    # Construct the visible polygon
    observer.snap_to_boundary_of(vis_environment, EPSILON)
    observer.snap_to_vertices_of(vis_environment, EPSILON)

    visible_polygon = Visibility_Polygon(observer, vis_environment, EPSILON)

    return Polygon([(visible_polygon[i].x(),
                     visible_polygon[i].y()) for i in range(visible_polygon.n())])
