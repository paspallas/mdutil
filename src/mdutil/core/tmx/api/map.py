from typing import List

import numpy as np

from mdutil.core.exceptions import *
from mdutil.core.tmx.model import BaseLayer, LayerType, Object, TmxMap
from mdutil.core.util import Size


class MapApi:
    def __init__(self, tmx_map: TmxMap) -> None:
        self._map = tmx_map

    def map_as_string(self) -> str:
        return str(self._map)

    def get_size_in_tile(self) -> Size:
        return Size(self._map.height, self._map.width)

    def get_size_in_px(self) -> Size:
        return Size(
            self._map.height * self._map.tile_height,
            self._map.width * self._map.tile_height,
        )

    def get_tile_size(self) -> Size:
        return Size(self._map.tile_height, self._map.tile_width)

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
        return self._map.layers[layer_type]

    def get_layer_by_name(self, layer_type: LayerType, name: str) -> BaseLayer:
        for layer in self.get_layers(layer_type):
            if layer.name == name:
                return layer

        raise TiledMapError(f"Layer '{name}' not found in the map file.")

    def get_tile(self, gid: int, priority) -> np.ndarray:
        for tileset in self._map.tilesets:
            if gid in tileset:
                return tileset.get_tile(gid, priority)

        raise TilesetError(f"Gid: {gid} not found in tileset collection.")
