# core/map.py
import json
from typing import Dict, Any, Optional, List
from .grid import BaseGrid


class MapData:
    """Container for generated map data using a sparse tile dictionary.

    Keys are coordinates (tuples); values are tile type strings.
    Unset coordinates are implicitly 'empty' / non-existent.
    """

    def __init__(self, grid: BaseGrid, seed: Optional[int] = None):
        self.grid = grid
        self.seed = seed
        self.tiles: Dict[Any, str] = {}
        self.metadata: Dict[str, Any] = {}

    # --- Tile access ---
    def set_tile(self, coord: Any, tile_type: str) -> None:
        if not self.grid.is_valid(coord):
            raise ValueError(f"Coordinate {coord} is outside the grid bounds.")
        self.tiles[coord] = tile_type

    def get_tile(self, coord: Any) -> Optional[str]:
        return self.tiles.get(coord)

    def has_tile(self, coord: Any) -> bool:
        return coord in self.tiles

    def remove_tile(self, coord: Any) -> None:
        self.tiles.pop(coord, None)

    # --- Bulk helpers (useful for generators) ---
    def set_tiles(self, coords: List[Any], tile_type: str) -> None:
        for coord in coords:
            self.set_tile(coord, tile_type)

    def get_tiles_by_type(self, tile_type: str) -> List[Any]:
        return [c for c, t in self.tiles.items() if t == tile_type]

    # --- Serialization ---
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary.

        Grid coordinates are stringified because JSON only supports string keys.
        The grid type and its parameters are recorded in metadata so the
        original grid can be reconstructed on load.
        """
        grid_params: Dict[str, Any] = {
            "type": self.grid.__class__.__name__,
        }
        # Capture grid-specific parameters for round-tripping.
        for attr in ("width", "height", "diagonal", "radius"):
            if hasattr(self.grid, attr):
                grid_params[attr] = getattr(self.grid, attr)

        return {
            "grid": grid_params,
            "seed": self.seed,
            "metadata": self.metadata,
            "tiles": {str(k): v for k, v in self.tiles.items()},
        }

    def save(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def __repr__(self) -> str:
        return f"MapData({self.grid!r}, tiles={len(self.tiles)})"

    def stats(self) -> dict:
        counts: dict = {}
        for tile in self.tiles.values():
            counts[tile] = counts.get(tile, 0) + 1
        return {
            "total_tiles": len(self.tiles),
            "by_type": counts,
            "grid": repr(self.grid),
            "seed": self.seed,
        }