from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw

from mdutil.core.exceptions import TilesetError
from mdutil.core.img.palette import Palette
from mdutil.core.util import Size


@dataclass
class BadTile:
    pos: Tuple[int]
    indexes: Tuple[int]
    rect: Tuple[int]

    def __str__(self) -> str:
        return f"  Tile at {self.pos} uses colors from palettes {self.indexes}"


class TileDebugger:
    def __init__(
        self,
        errors: List[BadTile],
        tileset: np.ndarray,
        path: str,
        palette: Palette,
    ):
        self.errors = errors
        self.path = path
        self.tileset_array = tileset
        self.pal = palette

    def generate_report(self) -> None:
        self._create_debug_tileset()

        error_messages = [str(error) for error in self.errors]
        raise TilesetError(
            "Bad tiles encountered in the tileset:\n {errors}\n\n  Created debug image: {path}".format(
                errors="\n".join(error_messages), path=self.path
            )
        )

    def _create_debug_tileset(self) -> None:
        with Image.fromarray(self.tileset_array, "P") as background:
            background.putpalette(self.pal.as_list())
            background = background.convert("RGBA")

            with Image.new("RGBA", background.size, (0, 0, 0, 0)) as overlay:
                draw = ImageDraw.Draw(overlay, mode="RGBA")
                for error in self.errors:
                    draw.rectangle(error.rect, fill=(255, 0, 0, 128))

                with Image.alpha_composite(background, overlay) as result:
                    path = f"{Path(self.path).stem}_error.png"

                    result.save(
                        path,
                        format="PNG",
                        optimize=True,
                    )


class TilesetImage:
    class Priority(Enum):
        LO = auto()
        HI = auto()

    def __init__(self, tile_size: Size, path: Path):
        """Create a tileset from a png image"""

        self.errors = []

        self.path = path
        self.tile_size = tile_size

        # Dictionary of tiles by priority
        self.tiles_hi: Dict[int, np.array] = {}
        self.tiles_lo: Dict[int, np.array] = {}

        self.tileset_array = self._load(path)
        self.palette = Palette(path)

        try:
            self.tiles_lo = self._extract_tiles(self.tileset_array, tile_size)
        except ValueError:
            debug = TileDebugger(
                self.errors, self.tileset_array, self.path, self.palette
            )
            debug.generate_report()

    def _load(self, img_path: str) -> np.ndarray:
        with Image.open(img_path) as img:
            if img.mode == "P":
                return np.array(img)

            raise TilesetError(
                f"Tileset image: {img_path} is not an indexed color image."
            )

    def _encode_hi_priority(self, tile_id: int) -> np.array:
        if tile_id in self.tiles_hi:
            return self.tiles_hi[tile_id]

        # Add 128 to all color indexes in the tile
        tile = self.tiles_lo[tile_id]
        tile = tile + 128

        self.tiles_hi[tile_id] = tile

        return tile

    def _extract_tiles(
        self, tileset_array: np.ndarray, tile_size: Size
    ) -> Dict[int, np.ndarray]:
        """Extracts all tile data from the tileset and creates a dictionary for fast tile indexing.

        Args:
            tileset_array (np.ndarray): color index data as an array
            tile_size (Size): tile size in pixels

        Raises:
            ValueError: Tiles can only use a single palette. An error is raised if a tile
            uses color indexes from more than one palette

        Returns:
            Dict[int, np.ndarray]: Dict of all tiles in the tileset using the tile_id as key and an
            array for the color index data
        """
        tileset_size = Size(*tileset_array.shape[:2])
        tiles_y, tiles_x = tileset_size // tile_size

        tiles: Dict[int, np.ndarray] = {}
        tile_id = 0

        for y in range(tiles_y):
            for x in range(tiles_x):
                x_start = x * tile_size.width
                y_start = y * tile_size.height

                tile = tileset_array[
                    y_start : y_start + tile_size.height,
                    x_start : x_start + tile_size.width,
                ].copy()

                pal_index = self.palette.get_index_for_tile(tile)
                if len(pal_index) > 1:
                    self.errors.append(
                        (
                            BadTile(
                                (x, y),
                                pal_index,
                                (
                                    x_start,
                                    y_start,
                                    x_start + tile_size.width - 1,
                                    y_start + tile_size.height - 1,
                                ),
                            )
                        )
                    )
                else:
                    tiles[tile_id] = tile
                    tile_id += 1

        if self.errors:
            raise ValueError

        return tiles

    def get_pal(self) -> np.ndarray:
        return self.palette.as_list()

    def get_tile(self, tile_id: int, priority: Priority) -> np.ndarray:
        if priority == TilesetImage.Priority.LO:
            return self.tiles_lo[tile_id]

        return self._encode_hi_priority(tile_id)
