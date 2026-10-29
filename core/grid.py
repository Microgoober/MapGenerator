# core/grid.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Any


class BaseGrid(ABC):
    """Abstract base class for all grid types.

    All concrete grids must implement neighbor lookup, distance,
    and bounds validation so generators can remain grid-agnostic.
    """

    @abstractmethod
    def get_neighbors(self, coord: Any) -> List[Any]:
        """Return a list of valid neighboring coordinates."""
        ...

    @abstractmethod
    def get_distance(self, coord_a: Any, coord_b: Any) -> int:
        """Return the distance between two coordinates (in grid steps)."""
        ...

    @abstractmethod
    def is_valid(self, coord: Any) -> bool:
        """Return True if the coordinate is within the grid's bounds."""
        ...


class SquareGrid(BaseGrid):
    """A standard 2D square grid.

    Coordinates are (x, y) integer tuples.
    Defaults to 4-way (von Neumann) neighbors for dungeon-style logic;
    pass diagonal=True for 8-way (Moore) neighbors.
    """

    def __init__(self, width: int, height: int, diagonal: bool = False):
        if width <= 0 or height <= 0:
            raise ValueError("Grid dimensions must be positive.")
        self.width = width
        self.height = height
        self.diagonal = diagonal

    def is_valid(self, coord: Tuple[int, int]) -> bool:
        try:
            x, y = coord
        except (TypeError, ValueError):
            return False
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(self, coord: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = coord
        if self.diagonal:
            candidates = [
                (x + dx, y + dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if not (dx == 0 and dy == 0)
            ]
        else:
            candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [c for c in candidates if self.is_valid(c)]

    def get_distance(self, coord_a: Tuple[int, int], coord_b: Tuple[int, int]) -> int:
        # Manhattan distance for 4-way; Chebyshev would be used for 8-way.
        if self.diagonal:
            return max(abs(coord_a[0] - coord_b[0]), abs(coord_a[1] - coord_b[1]))
        return abs(coord_a[0] - coord_b[0]) + abs(coord_a[1] - coord_b[1])

    def __repr__(self) -> str:
        return f"SquareGrid({self.width}x{self.height}, diagonal={self.diagonal})"


class HexGrid(BaseGrid):
    """A hex grid powered by the `hexpex` library.

    Internally uses axial coordinates (q, r). Public coords are (q, r) tuples,
    matching hexpex's AxialCoord convention.

    TODO: Once we confirm hexpex's API in a test run, this class will delegate
    neighbor/distance math to hexpex's AxialCoord helpers.
    """

    def __init__(self, radius: int):
        """
        radius: number of hexes from center to edge.
                Total tiles = 3*r*(r+1) + 1.
        """
        if radius < 0:
            raise ValueError("Radius must be non-negative.")
        self.radius = radius

        try:
            import hexpex  # noqa: F401
            self._hexpex_available = True
        except ImportError:
            self._hexpex_available = False

    def is_valid(self, coord: Tuple[int, int]) -> bool:
        # Axial hex validity within radius: max(|q|, |r|, |q+r|) <= radius
        try:
            q, r = coord
        except (TypeError, ValueError):
            return False
        return max(abs(q), abs(r), abs(q + r)) <= self.radius

    def get_neighbors(self, coord: Tuple[int, int]) -> List[Tuple[int, int]]:
        # Six axial directions (Red Blob Games / hexpex convention).
        q, r = coord
        directions = [(+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)]
        candidates = [(q + dq, r + dr) for dq, dr in directions]
        return [c for c in candidates if self.is_valid(c)]

    def get_distance(self, coord_a: Tuple[int, int], coord_b: Tuple[int, int]) -> int:
        # Hex distance in axial coordinates.
        aq, ar = coord_a
        bq, br = coord_b
        return (abs(aq - bq) + abs(ar - br) + abs((aq + ar) - (bq + br))) // 2

    def __repr__(self) -> str:
        return f"HexGrid(radius={self.radius})"