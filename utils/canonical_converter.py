"""Converter for convertring polygons to different representations."""
from shapely.geometry import Polygon


def shapely_poly_to_canonical(polygon: Polygon):
    """
    A simple helper function to convert a shapely object representing a polygon
    intop a cononical form polygon.

    Args:
        polygon: A shapely object representing a polygon

    Returns:
        A polygon in canonical form.
    """
    poly_exterior = list(polygon.exterior.coords)[::1 if polygon.exterior.is_ccw else -1]
    holes = [list(hole.coords)[::-1 if hole.is_ccw else 1] for hole in polygon.interiors]

    return [poly_exterior, holes]
