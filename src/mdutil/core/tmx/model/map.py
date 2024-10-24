import itertools
from pathlib import Path
from typing import Any, Dict, List, Union

from mdutil.core.exceptions import *
from mdutil.core.tmx.parser import *
from mdutil.core.util import Size, smart_repr

from .layer import BaseLayer, LayerType, ObjectLayer, TileLayer
from .object import Object


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

        return TmxMap.from_dict(parser.parse(path))


class TmxMap:
    def __init__(
        self,
        width: int,
        height: int,
        tile_width: int,
        tile_height: int,
        layers: Dict[LayerType, List[BaseLayer]],
    ) -> None:
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.layers = layers

    def get_size_in_tile(self) -> Size:
        return Size(self.height, self.width)

    def get_size_in_px(self) -> Size:
        return Size(self.height * self.tile_height, self.width * self.tile_height)

    def get_tile_size(self) -> Size:
        return Size(self.tile_height, self.tile_width)

    def get_object_by_id(self, id_: int) -> Object:
        for layers in self.get_layers(LayerType.OBJECT):
            for layer in layers:
                for obj in layer:
                    if obj.id_ == id_:
                        return obj

        raise TiledMapError(f"Object with id: {id_} not found in the map.")

    def get_object_by_name(self, name: str) -> Object:
        for layers in self.get_layers(LayerType.OBJECT):
            for layer in layers:
                for obj in layer:
                    if obj.name == name:
                        return obj

        raise TiledMapError(f"Object with name: {name} not found in the map.")

    def get_layers(self, layer_type: LayerType) -> List[BaseLayer]:
        return self.layers[layer_type]

    def get_layer_by_name(self, layer_type: LayerType, name: str) -> BaseLayer:
        for layer in self.get_layers(layer_type):
            if layer.name == name:
                return layer

        raise TiledMapError(f"Layer '{name}' not found in the map file.")

    def __len__(self) -> int:
        count = 0
        for _, layers in self.layers.items():
            count += len(layers)

        return count

    def __repr__(self) -> str:
        description = [smart_repr(self, exclude=("layers"))]
        for layers in self.layers.values():
            for layer in layers:
                description.append(f" -{str(layer)}")

        return "\n".join(description)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TmxMap":
        layers = {
            LayerType.TILE: [],
            LayerType.OBJECT: [],
        }

        for layer_data in data.get("layers", []):
            layer_type = layer_data["type"]
            if layer_type == "tilelayer":
                layers[LayerType.TILE].append(TileLayer.from_dict(layer_data))
            elif layer_type == "objectgroup":
                layers[LayerType.OBJECT].append(ObjectLayer.from_dict(layer_data))
            else:
                raise TiledMapError(f"Unsupported layer type {layer_type}")

        return cls(
            width=data.get("width", 0),
            height=data.get("height", 0),
            tile_width=data.get("tilewidth", 0),
            tile_height=data.get("tileheight", 0),
            layers=layers,
        )

    @classmethod
    def from_file(self, file_path: Union[str, Path]) -> "TmxMap":
        return TmxMapFactory().from_file(file_path)
