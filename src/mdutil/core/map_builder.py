from pathlib import Path
from typing import List, Optional, Tuple, Union

import click
import numpy as np
from PIL import Image

from mdutil.core.img.tileset import TilesetImage
from mdutil.core.tmx.api import MapApi
from mdutil.core.tmx.model import LayerType, TileLayer, TmxMap


class MapImageBuilder:
    def __init__(
        self,
        tiled_file_path: Union[str, Path],
    ) -> None:

        self.map_api = MapApi(TmxMap.from_file(tiled_file_path))

    def _build_tilemap_image(
        self, layers: List[Tuple[TileLayer, TilesetImage.Priority]]
    ) -> np.ndarray:

        map_height, map_width = self.map_api.get_size_in_px()
        tilemap_array = np.zeros((map_height, map_width), dtype=np.uint8)

        self.tile_size = self.map_api.get_tile_size()

        def stack_layer(layer: TileLayer, priority: TilesetImage.Priority) -> None:
            for i, gid in enumerate(layer):
                if gid == 0:
                    continue

                # Get the tile position in the composited image
                map_x = (i % layer.width) * self.tile_size.width
                map_y = (i // layer.width) * self.tile_size.height

                tilemap_array[
                    map_y : map_y + self.tile_size.height,
                    map_x : map_x + self.tile_size.width,
                ] = self.map_api.get_tile(gid, priority)

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
                    self.map_api.get_layer_by_name(LayerType.TILE, lo_layer),
                    TilesetImage.Priority.LO,
                ),
            )
        if hi_layer:
            stacked_layers.append(
                (
                    self.map_api.get_layer_by_name(LayerType.TILE, hi_layer),
                    TilesetImage.Priority.HI,
                )
            )

        try:
            with Image.fromarray(
                self._build_tilemap_image(stacked_layers), mode="P"
            ) as img:
                # TODO Fix me
                img.putpalette(self.map_api._map.tilesets[0].get_palette())
                img.save(output_path, format="PNG", optimize=False)

                click.echo(click.style(f"Saved '{output_path}'.", fg="green"))

        except OSError as e:
            raise OSError(
                f"Error while trying to save image file {output_path}."
            ) from e
