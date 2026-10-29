# generators/outdoor.py
"""Perlin-noise forest generator. Grid-agnostic: works on square and hex."""

import random
from typing import Optional

from perlin_noise import PerlinNoise

from core.grid import BaseGrid, SquareGrid, HexGridRect
from core.map import MapData


class OutdoorGenerator:
    """Generate a forest map with clearings, water, and scattered ruins."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed

    def generate_forest(
        self,
        grid: BaseGrid,
        scale: float = 0.12,
        octaves: int = 4,
    ) -> MapData:
        """Generate a forest map on the given grid.

        scale: coordinate multiplier for noise sampling. Larger = finer detail.
        """
        if not isinstance(grid, (SquareGrid, HexGridRect)):
            raise TypeError("OutdoorGenerator supports SquareGrid and HexGridRect.")

        # Deterministic seeds derived from self.seed.
        base_seed = self.seed if self.seed is not None else 0
        elev_noise = PerlinNoise(octaves=octaves, seed=base_seed)
        moist_noise = PerlinNoise(octaves=octaves, seed=base_seed + 1)

        mapdata = MapData(grid, seed=self.seed)
        mapdata.metadata.update({"mode": "outdoor", "theme": "forest"})

        rng = random.Random(self.seed)

        # Iterate the rectangular bounds. Works for both grid types
        # because SquareGrid uses (x, y) and HexGridRect uses (q, r).
        for x in range(grid.width):
            for y in range(grid.height):
                coord = (x, y)
                if not grid.is_valid(coord):
                    continue

                elevation = elev_noise([x * scale, y * scale])  # ~[-1, 1]
                moisture = moist_noise([x * scale, y * scale])

                # Normalize to [0, 1].
                elev_n = (elevation + 1.0) / 2.0
                moist_n = (moisture + 1.0) / 2.0

                tile = self._classify(elev_n, moist_n)

                # Scatter ruins in dense forest.
                if tile == "forest" and rng.random() < 0.02:
                    tile = "ruin"

                mapdata.set_tile(coord, tile)

        return mapdata

    @staticmethod
    def _classify(elevation: float, moisture: float) -> str:
        """Map normalized noise values to a tile type.

        Thresholds are tuned by eye; adjust freely.
        """
        if elevation < 0.35:
            return "water"
        if moisture > 0.55:
            return "forest"
        return "clearing"