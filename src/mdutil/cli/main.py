import click

from .genmap import genmap
from .version import version


@click.group()
@click.option(
    "--debug/--nodebug", default=False, help="Enable debug mode with full stack traces."
)
@click.pass_context
def cli(ctx, debug):
    """The swiss army knife for megadrive development"""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


# Register commands
cli.add_command(genmap)
cli.add_command(version)

if __name__ == "__main__":
    cli(obj={})
