import sys
import traceback
from functools import wraps
from pathlib import Path

import click
from tilemap import MapImageBuilder
from tileset import TilesetError
from version import __version__


def debug_exceptions(f):
    """Decorator to handle exceptions in debug mode"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            ctx = click.get_current_context()
            if ctx.obj.get("debug", False):
                click.echo(click.style("Traceback", fg="red", bold=True), err=True)
                click.echo(
                    click.style(
                        "".join(traceback.format_tb(e.__traceback__)), fg="red"
                    ),
                    err=True,
                )
                click.echo(
                    click.style(
                        f"\n{e.__class__.__name__}: {str(e)}", fg="red", bold=True
                    ),
                    err=True,
                )
                sys.exit(1)
            else:
                raise

    return wrapper


@click.group()
@click.option(
    "--debug/--nodebug", default=False, help="Enable debug mode with full stack traces."
)
@click.pass_context
def cli(ctx, debug):
    """The swiss army knife for megadrive development"""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@cli.command()
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
    Generate a png file that can be used as a sgdk MAP resource

    JSON_PATH: Path to the input tiled file\n
    TILESET_PATH: Path to the tileset image\n
    OUTPUT_PATH: Path to the output image
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
            click.echo(f"Reading from: {json_path}")

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


@cli.command()
def version():
    """Show detailed version information."""
    import platform

    import PIL

    click.echo(
        f"""
 mdutil v{__version__}
 Python {sys.version.split()[0]}
 Platform: {platform.platform()} 
 Pillow: {PIL.__version__}
    """.strip()
    )


if __name__ == "__main__":
    cli(obj={})
