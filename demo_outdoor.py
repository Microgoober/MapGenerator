# demo_outdoor.py
"""Demo: generate the same forest seed on a square grid and a hex grid."""

import os
from core.grid import SquareGrid, HexGridRect
from generators.outdoor import OutdoorGenerator
from renderers.ascii import render_ascii


def main():
    seed = 2024
    generator = OutdoorGenerator(seed=seed)

    square = generator.generate_forest(SquareGrid(40, 20))
    hexrect = generator.generate_forest(HexGridRect(40, 20))

    print("=== Square Grid Forest ===")
    print(render_ascii(square, empty_glyph=" "))
    print("\n=== Hex Rect Grid Forest ===")
    # Note: ASCII rendering of axial hex still prints one char per (q, r)
    # cell in a rectangular block; true staggered hex ASCII is a future commit.
    print(render_ascii(hexrect, empty_glyph=" "))

    os.makedirs("output", exist_ok=True)
    square.save("output/forest_square.json")
    hexrect.save("output/forest_hex.json")
    print("\nSaved: output/forest_square.json, output/forest_hex.json")


if __name__ == "__main__":
    main()