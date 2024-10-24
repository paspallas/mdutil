from pathlib import Path

import click

from mdutil.core import (
    MapBuilderError,
    MapImageBuilder,
    PropertyError,
    TiledMapError,
    TileLayerError,
    TilesetError,
)

from .params import ParameterPair
from .utils import debug_exceptions


def validate_layer_id(id_: str, lo: str, hi: str):
    if id_ not in ("bga", "bgb"):
        raise click.BadParameter(
            f"Invalid plane identifier: '{id_}'. Options [bga, bgb]."
        )


@click.command()
@click.argument(
    "tiled_file_path", type=click.Path(exists=True, dir_okay=True, path_type=Path)
)
@click.argument(
    "output_folder", type=click.Path(exists=False, dir_okay=True, path_type=Path)
)
@click.option(
    "--layer",
    "-l",
    type=ParameterPair(value_types=(str, str), validator=validate_layer_id),
    multiple=True,
    help="Plane to export in the format 'bg[a,b]=lo_prio_layer_name,hi_prio_layer_name'. Use '_' for excluding a layer from the export.",
)
@click.pass_context
@debug_exceptions
def genmap(
    ctx,
    tiled_file_path: Path,
    output_folder: Path,
    layer: ParameterPair,
):
    """
    Generate a (pair) png file that can be used as a SGDK MAP resource from a tiled file

    TILED_FILE_PATH: Path to the input tiled file in json or tmx format\n
    OUTPUT_FOLDER: Path to the output folder
    """
    try:
        # Create output directory if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / tiled_file_path.stem

        builder = MapImageBuilder(tiled_file_path)

        for id_val, lo, hi in layer:
            lo_layer = lo if lo != "_" else None
            hi_layer = hi if hi != "_" else None

            if id_val == "bgb":
                output = f"{output_path}_BGB.png"
            elif id_val == "bga":
                output = f"{output_path}_BGA.png"

            builder.save(output, lo_layer, hi_layer)

    except click.UsageError as e:
        raise click.UsageError(str(e))
    except MapBuilderError as e:
        raise click.ClickException(f"Map build error: {str(e)}")
    except PropertyError as e:
        raise click.ClickException(f"Property error: {str(e)}")
    except TilesetError as e:
        raise click.ClickException(f"Tileset error: {str(e)}")
    except TileLayerError as e:
        raise click.ClickException(f"Tilelayer error: {str(e)}")
    except TiledMapError as e:
        raise click.ClickException(f"Tiled map error: {str(e)}")
    except Exception as e:
        if ctx.obj["debug"]:
            raise
        else:
            click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
