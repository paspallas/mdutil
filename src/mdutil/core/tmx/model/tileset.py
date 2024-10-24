from typing import Any, Dict

from mdutil.core.util import smart_repr


class Tileset:
    def __init__(
        self,
        columns: int,
        first_gid: int,
        image: str,
        name: str,
        spacing: int,
        tile_count: int,
        tile_height: int,
        tile_width: int,
    ) -> None:
        self.columns = columns
        self.first_gid = first_gid
        self.image = image
        self.name = name
        self.spacing = spacing
        self.tile_count = tile_count
        self.tile_height = tile_height
        self.tile_width = tile_width

    def __repr__(self) -> str:
        return smart_repr(
            self,
            (
                "spacing",
                "columns",
                "tile_height",
                "tile_width",
            ),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tileset":
        return cls(
            columns=data.get("columns", 0),
            first_gid=data.get("first_gid", 0),
            image=data.get("image", ""),
            name=data.get("name", ""),
            spacing=data.get("spacing", 0),
            tile_count=data.get("tilecount", 0),
            tile_height=data.get("tileheight", 0),
            tile_width=data.get("tilewidth", 0),
        )
