import base64
import json
import zlib
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image
from tileset import Tileset
from util import Size


class MapImageBuilder:
    def __init__(
        self,
        json_path: str,
        tileset_path: str,
        lo_layer: str = "LO",
        hi_layer: str = "HI",
    ) -> None:

        if not Path(json_path).exists():
            raise FileNotFoundError(f"Error: json file '{json_path}' not found.")

        if not Path(tileset_path).exists():
            raise FileNotFoundError(f"Error: tileset image '{tileset_path}' not found.")

        self.lo_layer_name = lo_layer
        self.hi_layer_name = hi_layer

        self.tiled_data = self._load_json(json_path)
        self.tile_size = Size(
            self.tiled_data["tileheight"], self.tiled_data["tilewidth"]
        )
        self.map_size_tile = Size(self.tiled_data["height"], self.tiled_data["width"])
        self.map_size_px = self.map_size_tile * self.tile_size

        self._tileset = Tileset(self.tile_size, tileset_path)
        self._tilemap = self._build_tilemap()

    def _load_json(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _decode_tile_layer(self, data: str) -> List[int]:
        return np.frombuffer(
            zlib.decompress(base64.b64decode(data)), dtype=np.uint32
        ).tolist()

    def _build_tilemap(self) -> np.ndarray:
        tilemap_array = np.zeros(
            (self._map_height_px, self._map_width_px),
            dtype=np.uint8,
        )

        def stack_layer(
            layer: List[int], width: int, priority: Tileset.Priority
        ) -> None:
            for i, tile_id in enumerate(layer):
                if tile_id == 0:
                    continue

                # Get position
                map_x = (i % width) * self._tile_width
                map_y = (i // width) * self._tile_height

                # Place tile inside array bounds
                if (
                    map_y + self._tile_height <= tilemap_array.shape[0]
                    and map_x + self._tile_width <= tilemap_array.shape[1]
                ):
                    tilemap_array[
                        map_y : map_y + self._tile_height,
                        map_x : map_x + self._tile_width,
                    ] = self._tileset.get_tile(tile_id - 1, priority)

        for layer in self.tiled_data["layers"]:
            if layer["type"] == "tilelayer":
                layer_name = layer["name"]
                layer_width = layer["width"]
                if layer_name == self.lo_layer_name:
                    priority = Tileset.Priority.LO
                elif layer_name == self.hi_layer_name:
                    priority = Tileset.Priority.HI
                else:
                    continue

                stack_layer(
                    self._decode_tile_layer(layer["data"]),
                    layer_width,
                    priority,
                )

        return tilemap_array

    def save(self, path: str) -> None:
        with Image.fromarray(self._build_tilemap(), mode="P") as img:
            img.putpalette(self._tileset.get_pal())
            img.save(path, format="PNG", optimize=False)