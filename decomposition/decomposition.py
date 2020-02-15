"""Defining decomposition class for single agent decomposition."""
from copy import deepcopy
from typing import Dict, List, Tuple

from shapely.geometry import Polygon, Point

from utils import shapely_poly_to_canonical


class Decomposition():
    """Container class for storing decomposition for single agent coverage path planning."""
    __slots__ = (
        'polygon',
        'canonical_polygon',
        'num_cells',
        'canonical_cells',
        'cells',
    )

    def __init__(self, polygon: List[List]):
        """
        Args:
            polygon (List): Polygon in its canonical form.
        """
        self.canonical_polygon = deepcopy(polygon)
        self.polygon = Polygon(*polygon)

        self.num_cells = 0

        self.canonical_cells: Dict[int, List] = {}
        self.cells: Dict[int, Polygon] = {}

    def add_cell(self, cell: List[List]) -> int:
        """Adds a cell to the decomposition and returns its assigned index.

        Args:
            cell (List): List of veritcies.
        Returns:
            index assigned to this cell.
        """
        self.canonical_cells[self.num_cells] = deepcopy(cell)
        self.cells[self.num_cells] = Polygon(*cell)

        self.num_cells += 1

        return self.num_cells - 1

    def __getitem__(self, key: int) -> Tuple[Polygon, Point]:
        """Override getitem."""
        # TODO: Implement checks.
        return self.cells[key]

    def __setitem__(self, key: int, val: Polygon):
        self.cells[key] = val
        self.canonical_cells[key] = shapely_poly_to_canonical(val)

    def items(self) -> List:
        return self.cells.items()
