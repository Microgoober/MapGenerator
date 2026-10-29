# renderers/ascii.py
"""ASCII renderer for MapData. Prints a map to the terminal."""

from core.map import MapData
from core.grid import SquareGrid, HexGrid, HexGridRect


# Display glyph per tile type. Extend as we add more tile types.
TILE_GLYPHS = {
    "wall": "#",
    "floor": ".",
    "door": "+",
    "stairs": ">",
    "forest": "♣",
    "tree": "♣",
    "clearing": "·",
    "ruin": "R",
    "water": "~",
    "road": "=",
    "building": "□",
}


def render_ascii(mapdata: MapData, empty_glyph: str = " ") -> str:
    """Render a MapData to an ASCII string.

    Currently supports SquareGrid. HexGrid support will be added
    when we build the world/outdoor generators.
    """
    if isinstance(mapdata.grid, (SquareGrid, HexGridRect)):
        return _render_square(mapdata, empty_glyph)
    if isinstance(mapdata.grid, HexGrid):
        raise NotImplementedError("Hex ASCII rendering is a future commit.")
    raise TypeError(f"Unsupported grid type: {type(mapdata.grid).__name__}")


def _render_square(mapdata: MapData, empty_glyph: str) -> str:
    grid = mapdata.grid
    lines = []
    for y in range(grid.height):
        row = []
        for x in range(grid.width):
            tile = mapdata.get_tile((x, y))
            row.append(TILE_GLYPHS.get(tile, empty_glyph))
        lines.append("".join(row))
    return "\n".join(lines)