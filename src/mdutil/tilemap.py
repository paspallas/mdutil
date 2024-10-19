import base64
import json
import zlib
from typing import List

import click
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

        self.lo_layer_name = lo_layer
        self.hi_layer_name = hi_layer

        self.tiled_data = self._load_json(json_path)
        self.tile_size = Size(
            self.tiled_data["tileheight"], self.tiled_data["tilewidth"]
        )
        self.map_size_tile = Size(self.tiled_data["height"], self.tiled_data["width"])
        self.map_size_px = self.map_size_tile * self.tile_size

        self.tileset = Tileset(self.tile_size, tileset_path)
        self.tilemap = self._build_tilemap()

    def _load_json(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _decode_tile_layer(self, data: str) -> List[int]:
        return np.frombuffer(
            zlib.decompress(base64.b64decode(data)), dtype=np.uint32
        ).tolist()

    def _build_tilemap(self) -> np.ndarray:
        tilemap_array = np.zeros(
            (self.map_size_px.height, self.map_size_px.width),
            dtype=np.uint8,
        )

        def stack_layer(
            layer: List[int], width: int, priority: Tileset.Priority
        ) -> None:
            for i, tile_id in enumerate(layer):
                if tile_id == 0:
                    continue

                # Get position
                map_x = (i % width) * self.tile_size.width
                map_y = (i // width) * self.tile_size.height

                # Place tile inside array bounds
                if (
                    map_y + self.tile_size.height <= tilemap_array.shape[0]
                    and map_x + self.tile_size.width <= tilemap_array.shape[1]
                ):
                    tilemap_array[
                        map_y : map_y + self.tile_size.height,
                        map_x : map_x + self.tile_size.width,
                    ] = self.tileset.get_tile(tile_id - 1, priority)

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
        try:
            with Image.fromarray(self._build_tilemap(), mode="P") as img:
                img.putpalette(self.tileset.get_pal())
                img.save(path, format="PNG", optimize=False)

                click.echo(click.style(f"\nSaved '{path}' file.", fg="green"))

        except OSError as e:
            raise OSError(f"Error while trying to save image file {path}.") from e
