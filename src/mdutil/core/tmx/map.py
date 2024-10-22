import json
from typing import Any, Dict, List

from mdutil.core.exceptions import *
from mdutil.core.util import Size

from .layer import BaseLayer, LayerType, ObjectLayer, TileLayer


class Map:
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
        description = [
            f" Map(w={self.width}, h={self.height}, tw={self.tile_width}, th={self.tile_height} layers={len(self)})"
        ]
        for layers in self.layers.values():
            for layer in layers:
                description.append(f" -{str(layer)}")

        return "\n".join(description)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Map":
        layers = {
            LayerType.TILE: [],
            LayerType.OBJECT: [],
        }

        for layer_data in data.get("layers", []):
            layer_type = layer_data["type"]
            if layer_type == "tilelayer":
                layers[LayerType.TILE].append(TileLayer.from_json(layer_data))
            elif layer_type == "objectgroup":
                layers[LayerType.OBJECT].append(ObjectLayer.from_json(layer_data))
            else:
                raise TiledMapError(f"Unsupported layer type {layer_type}")

        return cls(
            width=data.get("width", 0),
            height=data.get("height", 0),
            tile_width=data.get("tilewidth", 0),
            tile_height=data.get("tileheight", 0),
            layers=layers,
        )

    @staticmethod
    def parse_tiled_json(json_file: str) -> "Map":
        with open(json_file, "r", encoding="utf-8") as file:
            return Map.from_json(json.load(file))
