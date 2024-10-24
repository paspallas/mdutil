from pathlib import Path
from typing import List, Optional, Tuple, Union

import click
import numpy as np
from PIL import Image

from mdutil.core.tileset import Tileset
from mdutil.core.tmx import LayerType, MapFactory, TileLayer


class MapImageBuilder:
    def __init__(
        self,
        tiled_file_path: Union[str, Path],
        tileset_path: str,
    ) -> None:

        self.map = MapFactory().from_file(tiled_file_path)
        print(self.map)
        self.tile_size = self.map.get_tile_size()
        self.tileset = Tileset(self.tile_size, tileset_path)

    def _build_tilemap_image(
        self, layers: List[Tuple[TileLayer, Tileset.Priority]]
    ) -> np.ndarray:
        map_size = self.map.get_size_in_px()
        tilemap_array = np.zeros((map_size.height, map_size.width), dtype=np.uint8)

        def stack_layer(layer: TileLayer, priority: Tileset.Priority) -> None:
            for i, tile_id in enumerate(layer):
                if tile_id == 0:
                    continue

                # Get the tile position in the composited image
                map_x = (i % layer.width) * self.tile_size.width
                map_y = (i // layer.width) * self.tile_size.height

                tilemap_array[
                    map_y : map_y + self.tile_size.height,
                    map_x : map_x + self.tile_size.width,
                ] = self.tileset.get_tile(tile_id, priority)

        for layer in layers:
            stack_layer(
                layer[0],
                layer[1],
            )

        return tilemap_array

    def save(
        self,
        output_path: str,
        lo_layer: Optional[str] = None,
        hi_layer: Optional[str] = None,
    ) -> None:

        stacked_layers = []
        if lo_layer:
            stacked_layers.append(
                (
                    self.map.get_layer_by_name(LayerType.TILE, lo_layer),
                    Tileset.Priority.LO,
                ),
            )
        if hi_layer:
            stacked_layers.append(
                (
                    self.map.get_layer_by_name(LayerType.TILE, hi_layer),
                    Tileset.Priority.HI,
                )
            )

        try:
            with Image.fromarray(
                self._build_tilemap_image(stacked_layers), mode="P"
            ) as img:
                img.putpalette(self.tileset.get_pal())
                img.save(output_path, format="PNG", optimize=False)

                click.echo(click.style(f"Saved '{output_path}'.", fg="green"))

        except OSError as e:
            raise OSError(
                f"Error while trying to save image file {output_path}."
            ) from e
