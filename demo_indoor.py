# demo_indoor.py
"""End-to-end demo: generate, render, and save a dungeon."""

import os
from generators.indoor import IndoorGenerator
from renderers.ascii import render_ascii


def main():
    generator = IndoorGenerator(seed=1234)

    # Generate a 3-story building.
    floors = generator.generate(width=40, height=20, stories=3)

    print(f"Generated {len(floors)} stories.\n")

    for i, floor in enumerate(floors):
        floor_count = len(floor.get_tiles_by_type("floor"))
        wall_count = len(floor.get_tiles_by_type("wall"))
        print(f"=== Story {i + 1} ===")
        print(f"  floor tiles: {floor_count}, wall tiles: {wall_count}")
        print(render_ascii(floor, empty_glyph=" "))
        print()

    # Save all floors.
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    for i, floor in enumerate(floors):
        path = os.path.join(out_dir, f"indoor_story_{i + 1}.json")
        floor.save(path)
        print(f"Saved: {path}")


if __name__ == "__main__":
    main()