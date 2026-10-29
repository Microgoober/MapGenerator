# generators/indoor.py
"""Indoor map generator, backed by the `dungy` library.

`dungy` produces a 2D ASCII grid of characters:
    '#' = wall, '.' = floor, ' ' = empty space

We translate that into our sparse MapData dictionary using the
tile vocabulary shared by all generators:
    "wall", "floor", "door", "stairs", "empty"
"""

import random
from typing import Optional

from dungy import DungeonGenerator

from core.grid import SquareGrid
from core.map import MapData


# Map dungy's ASCII characters to our tile type strings.
DUNGY_CHAR_TO_TILE = {
    "#": "wall",
    ".": "floor",
    " ": "empty",
}


class IndoorGenerator:
    """Generate a single-story dungeon using dungy.

    dungy is inherently square-grid based. For multi-story buildings
    we simply generate N independent stories and return them as a
    list of MapData (as agreed: stories are stacked, not interconnected).
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self._rng = random.Random(seed)

    def generate(
        self,
        width: int = 30,
        height: int = 20,
        stories: int = 1,
    ) -> list[MapData]:
        """Generate `stories` independent dungeon floors.

        Returns a list of MapData, index 0 = ground floor.
        """
        if stories < 1:
            raise ValueError("stories must be >= 1")

        floors: list[MapData] = []
        for story_index in range(stories):
            # Derive a per-story seed so stories are reproducible but distinct.
            story_seed = None if self.seed is None else self.seed + story_index
            floors.append(self._generate_one(width, height, story_seed, story_index))
        return floors

    def _generate_one(
        self,
        width: int,
        height: int,
        story_seed: Optional[int],
        story_index: int,
    ) -> MapData:
        # dungy expects an rng=random.Random(...) instance.
        rng = random.Random(story_seed)
        generator = DungeonGenerator(
            width=width,
            height=height,
            rng=rng,
        )
        generator.generate()

        grid = SquareGrid(width, height)
        mapdata = MapData(grid, seed=story_seed)
        mapdata.metadata.update({
            "mode": "indoor",
            "theme": "dungeon",
            "story_index": story_index,
            "story_count_label": f"story {story_index + 1}",
        })

        # dungy exposes the internal 2D grid as a list of strings.
        # We iterate and translate each character into a tile.
        for y, row in enumerate(generator.render()):
            for x, char in enumerate(row):
                tile = DUNGY_CHAR_TO_TILE.get(char, "empty")
                mapdata.set_tile((x, y), tile)

        return mapdata