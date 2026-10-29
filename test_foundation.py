# test_foundation.py
"""Smoke test for the core grid + map foundation."""

import random
from core.grid import SquareGrid, HexGrid
from core.map import MapData


def test_square_grid_basic():
    grid = SquareGrid(10, 10)
    # Corner has 2 neighbors (4-way).
    assert len(grid.get_neighbors((0, 0))) == 2
    # Center has 4 neighbors.
    assert len(grid.get_neighbors((5, 5))) == 4
    # Edge has 3 neighbors.
    assert len(grid.get_neighbors((0, 5))) == 3
    # Distance check.
    assert grid.get_distance((0, 0), (3, 4)) == 7
    # Invalid coord.
    assert not grid.is_valid((-1, 0))
    assert not grid.is_valid((10, 0))
    print("✓ SquareGrid basic tests passed")


def test_square_grid_diagonal():
    grid = SquareGrid(10, 10, diagonal=True)
    assert len(grid.get_neighbors((0, 0))) == 3
    assert len(grid.get_neighbors((5, 5))) == 8
    print("✓ SquareGrid diagonal tests passed")


def test_hex_grid_basic():
    grid = HexGrid(radius=3)
    # Center has 6 neighbors.
    assert len(grid.get_neighbors((0, 0))) == 6
    # Distance of same point is 0.
    assert grid.get_distance((0, 0), (0, 0)) == 0
    # Adjacent hexes are distance 1.
    assert grid.get_distance((0, 0), (1, 0)) == 1
    # Distance across two steps.
    assert grid.get_distance((0, 0), (2, 0)) == 2
    print("✓ HexGrid basic tests passed")


def test_map_data_roundtrip(tmp_path=None):
    # Build a small square map with forest tiles.
    grid = SquareGrid(6, 6)
    mapdata = MapData(grid, seed=42)
    mapdata.metadata["mode"] = "outdoor"
    mapdata.metadata["theme"] = "forest"

    # Track unique coords explicitly: random draws can collide.
    rng = random.Random(42)
    expected_coords = set()
    for _ in range(15):
        coord = (rng.randrange(6), rng.randrange(6))
        mapdata.set_tile(coord, "forest")
        expected_coords.add(coord)

    # Sparse dict: size equals number of UNIQUE coordinates.
    assert len(mapdata.tiles) == len(expected_coords)
    assert len(mapdata.tiles) <= 15  # sanity: never more than draws
    # Every expected coord is present.
    for coord in expected_coords:
        assert mapdata.get_tile(coord) == "forest"

    # Verify round-trip to dict.
    d = mapdata.to_dict()
    assert d["grid"]["type"] == "SquareGrid"
    assert d["grid"]["width"] == 6
    assert d["seed"] == 42
    assert d["metadata"]["theme"] == "forest"
    assert len(d["tiles"]) == len(expected_coords)
    # All tile keys should be strings in the serialized form.
    assert all(isinstance(k, str) for k in d["tiles"].keys())

    # Save + reload to confirm file I/O works.
    import tempfile, os, json
    path = os.path.join(tempfile.gettempdir(), "test_map.json")
    mapdata.save(path)
    with open(path) as f:
        reloaded = json.load(f)
    assert reloaded == d
    os.remove(path)
    print(f"✓ MapData round-trip tests passed ({len(expected_coords)} unique tiles from 15 draws)")

def test_hex_map():
    grid = HexGrid(radius=2)
    mapdata = MapData(grid, seed=7)
    mapdata.set_tile((0, 0), "ruins")
    mapdata.set_tile((1, 0), "ruins")
    assert mapdata.get_tile((0, 0)) == "ruins"
    assert mapdata.get_tiles_by_type("ruins") == [(0, 0), (1, 0)]
    print("✓ HexGrid map integration passed")


def check_hexpex_available():
    try:
        import hexpex
        print(f"✓ hexpex is installed (version info: {getattr(hexpex, '__version__', 'n/a')})")
        return True
    except ImportError:
        print("✗ hexpex NOT installed. Run: pip install hexpex")
        return False


if __name__ == "__main__":
    print("Running core foundation tests...\n")
    check_hexpex_available()
    test_square_grid_basic()
    test_square_grid_diagonal()
    test_hex_grid_basic()
    test_map_data_roundtrip()
    test_hex_map()
    print("\nAll foundation tests passed.")