from pathlib import Path
from typing import Any, Dict

import numpy as np

from mdutil.core.img import TilesetImage
from mdutil.core.util import Size, smart_repr


class Tileset:
    def __init__(
        self,
        base_path: Path,
        columns: int,
        first_gid: int,
        image_name: str,
        name: str,
        spacing: int,
        margin: int,
        tile_count: int,
        tile_height: int,
        tile_width: int,
    ) -> None:
        self.base_path = base_path
        self.columns = columns
        self.first_gid = first_gid
        self.image_name = image_name
        self.name = name
        self.spacing = spacing
        self.margin = margin
        self.tile_count = tile_count
        self.tile_height = tile_height
        self.tile_width = tile_width

        self._load_image()

    def _load_image(self) -> None:
        img_path = self.base_path.resolve().parent / self.image_name

        self._tileset_image = TilesetImage(
            Size(self.tile_height, self.tile_width), img_path
        )

    def get_tile(self, gid: int, priority: TilesetImage.Priority) -> np.ndarray:
        return self._tileset_image.get_tile(gid - self.first_gid, priority)

    def get_palette(self) -> np.ndarray:
        return self._tileset_image.get_pal()

    def __contains__(self, gid: int) -> bool:
        last_gid = self.first_gid + self.tile_count
        return self.first_gid <= gid <= last_gid

    def __repr__(self) -> str:
        return smart_repr(
            self,
            (
                "margin",
                "spacing",
                "columns",
                "tile_height",
                "tile_width",
            ),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any], base_path: Path) -> "Tileset":
        return cls(
            base_path=base_path,
            columns=data.get("columns", 0),
            first_gid=data.get("firstgid", 0),
            image_name=data.get("image", ""),
            name=data.get("name", ""),
            spacing=data.get("spacing", 0),
            margin=data.get("margin", 0),
            tile_count=data.get("tilecount", 0),
            tile_height=data.get("tileheight", 0),
            tile_width=data.get("tilewidth", 0),
        )
