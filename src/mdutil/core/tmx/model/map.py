from pathlib import Path
from typing import Any, Dict, List, Union

from mdutil.core.exceptions import *
from mdutil.core.tmx.parser import *
from mdutil.core.util import Size, smart_repr

from .layer import BaseLayer, LayerType, ObjectLayer, TileLayer
from .tileset import Tileset


class TmxMapFactory:
    def __init__(self) -> None:
        self.parsers: Dict[str, TmxParser] = {
            ".json": JsonTmxParser(),
            ".tmj": JsonTmxParser(),
            ".tmx": XmlTmxParser(),
            ".xml": XmlTmxParser(),
        }

    def from_file(self, file_path: Union[str, Path]) -> "TmxMap":
        path = Path(file_path)
        parser = self.parsers.get(path.suffix.lower())
        if not parser:
            raise TiledMapError(f"Unrecognized file format: {path}")

        content = parser.parse(path)
        content["path"] = path
        return TmxMap.from_dict(content)


class TmxMap:
    def __init__(
        self,
        width: int,
        height: int,
        tile_width: int,
        tile_height: int,
        layers: Dict[LayerType, List[BaseLayer]],
        tilesets: List[Tileset],
        path: Path,
    ) -> None:
        self.path = path
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.layers = layers
        self.tilesets = tilesets

    def __len__(self) -> int:
        count = 0
        for _, layers in self.layers.items():
            count += len(layers)

        return count

    def __repr__(self) -> str:
        description = [smart_repr(self, exclude=("layers", "tilesets"))]
        for layers in self.layers.values():
            for layer in layers:
                description.append(f" -{str(layer)}")

        for tileset in self.tilesets:
            description.append(f" ^{str(tileset)}")

        return "\n".join(description)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TmxMap":
        layers = {
            LayerType.TILE: [],
            LayerType.OBJECT: [],
        }

        tilesets = []

        for layer_data in data.get("layers", []):
            layer_type = layer_data["type"]
            if layer_type == "tilelayer":
                layers[LayerType.TILE].append(TileLayer.from_dict(layer_data))
            elif layer_type == "objectgroup":
                layers[LayerType.OBJECT].append(ObjectLayer.from_dict(layer_data))
            else:
                raise TiledMapError(f"Unsupported layer type {layer_type}")

        for tileset_data in data.get("tilesets", []):
            tilesets.append(Tileset.from_dict(tileset_data, data.get("path")))

        return cls(
            path=data.get("path", None),
            width=data.get("width", 0),
            height=data.get("height", 0),
            tile_width=data.get("tilewidth", 0),
            tile_height=data.get("tileheight", 0),
            layers=layers,
            tilesets=tilesets,
        )

    @classmethod
    def from_file(self, file_path: Union[str, Path]) -> "TmxMap":
        return TmxMapFactory().from_file(file_path)
