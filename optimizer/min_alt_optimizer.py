"""Module for minimum altitude decomposition of polygons."""
from typing import List, Tuple

from shapely.geometry import LineString, LinearRing, Polygon, MultiLineString

from decomposition.decomposition import Decomposition, stage_cut, cut
from altitudes.altitude import get_min_altitude


def is_reflex(prev_vert: Tuple[float, float],
              mid_vert: Tuple[float, float],
              next_vert: Tuple[float, float]) -> bool:
    """Method for checking if three verts are reflex or not.

    Args:
        prev_vert (Tuple[float]): First vertex in a sequence.
        mid_vert (Tuple[float]): Second vertex in a sequence.
        next_vert (Tuple[float]): Third vertex in a sequence.

    Returns:
        True if the sequence is reflex.
    """
    dx_1, dx_2 = mid_vert[0] - next_vert[0], prev_vert[0] - mid_vert[0]
    dy_1, dy_2 = mid_vert[1] - next_vert[1], prev_vert[1] - mid_vert[1]
    return dx_1 * dy_2 - dy_1 * dx_2 > 0.0


def vertex_sampler(decomposition: Decomposition) -> List[LineString]:
    """
    One of the simple samplers that generates cuts that originate at a reflex vertex and end
    at some vertex of a polygon.

    Args:
        decomposition (Decomposition): An instance of decomposition.

    Returns:
        A list of valid cuts.
    """
    reflex_verts = get_cut_origins(decomposition)
    orig_poly = decomposition.orig_polygon

    coords: List[Tuple[float, float]] = []
    for chain in [orig_poly.exterior, *orig_poly.interiors]:
        coords.extend(chain.coords[:-1])

    samples = [LineString((x, y)) for x in reflex_verts for y in coords]

    final_list = []
    for sample in samples:
        common_pts = orig_poly.exterior.intersection(sample)

        if not (common_pts.is_empty or
                not common_pts.geom_type == 'MultiPoint' or # Intersection should be MultiPoint.
                len(common_pts) != 2 or # MultiPoint must ONLY have 2 points.
                not sample.within(orig_poly) or # Split line should be inside cell.
                any(sample.intersects(hole) for hole in orig_poly.interiors)): # Cut touching holes?
            final_list.append(sample)

    return final_list


def get_cut_origins(decomposition: Decomposition) -> List[Tuple[float, float]]:
    """Find all reflex vertecies in the polygon.

    Args:
        decomposition (Decomposition): Instance of a decomposition.

    Returns:
        List of reflex vertices in the decomposition.
    """
    reflex_verts: List[Tuple[float, float]] = []
    for cell in decomposition.cells:
        for chain in [cell.exterior, *cell.interiors]:
            points = chain.coords[:-1]
            for i, _ in enumerate(points):
                if is_reflex((points[i - 1]), points[i], points[(i + 1) % len(points)]):
                    reflex_verts.append(points[i])
    return reflex_verts


def min_alt_optimize(decomposition: Decomposition, samples: List[LineString]):
    """Simple optimizer that iterates over the sample space and performs improvements.

    Note:
        Modifies decomposition argument.
        Modifies samples argument.

        This implementation is LAZY. The first improving cut for a origin vertex will be taken.
        TODO: Implement a search over all samples for best cuts.

    Args:
        decomposition (Decomposition): An instance of decomposition object. If a cut is performed,
                                       decomposition is modified accordingly.
        samples (List): A list of samples to optimize over. If a cut is performed for a sample,
                        that sample is removed from samples.
    """
    while samples:
        sample = samples.pop()
        orig_cell, res_p1, res_p2 = stage_cut(decomposition, sample)

        if not orig_cell:
            continue

        orig_p_alt, _ = get_min_altitude(orig_cell)
        res_p1_alt, _ = get_min_altitude(res_p1)
        res_p2_alt, _ = get_min_altitude(res_p2)

        if res_p2_alt + res_p1_alt < orig_p_alt:
            print("Improved cut from {} vs {}".format(orig_p_alt,
                                                      res_p1_alt + res_p2_alt))
            cut(decomposition, sample)
