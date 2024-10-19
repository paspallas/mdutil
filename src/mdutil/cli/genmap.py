from pathlib import Path

import click

from mdutil.core import MapImageBuilder, TilesetError

from .utils import debug_exceptions


@click.command()
@click.argument(
    "json_path", type=click.Path(exists=True, dir_okay=True, path_type=Path)
)
@click.argument(
    "tileset_path", type=click.Path(exists=True, dir_okay=True, path_type=Path)
)
@click.argument(
    "output_path", type=click.Path(exists=False, dir_okay=True, path_type=Path)
)
@click.option(
    "--lo-layer-name", "-l", type=str, default="LO", help="Lo priority layer name."
)
@click.option(
    "--hi-layer-name", "-h", type=str, default="HI", help="Hi priority layer name."
)
@click.option(
    "--force", "-f", is_flag=True, help="Overwrite output files if they exist."
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Print detailed progress information."
)
@click.pass_context
@debug_exceptions
def genmap(
    ctx,
    json_path: Path,
    tileset_path: Path,
    output_path: Path,
    lo_layer_name: str,
    hi_layer_name: str,
    force: bool,
    verbose: bool,
):
    """
    Generate a png file that can be used as a SGDK MAP resource.

    JSON_PATH: Path to the input tiled file\n.
    TILESET_PATH: Path to the tileset image\n.
    OUTPUT_PATH: Path to the output image.
    """
    try:
        # Check if output tiles exist
        if not force:
            if output_path.exists():
                raise click.UsageError(
                    f"Ouput file exists: {output_path}. Use --force to overwrite."
                )

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if verbose:
            click.echo("Starting tiled file conversion...")
            click.echo(f"Reading from: '{json_path}'")

        builder = MapImageBuilder(
            json_path.as_posix(), tileset_path.as_posix(), lo_layer_name, hi_layer_name
        )
        builder.save(output_path.as_posix())

    except click.UsageError as e:
        raise click.UsageError(str(e))
    except TilesetError as e:
        raise click.ClickException(f"Tileset error: {str(e)}")
    except Exception as e:
        if ctx.obj["debug"]:
            raise
        else:
            click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
