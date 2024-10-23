import sys

import click

from mdutil.version import __version__


@click.command()
def version():
    """Show detailed version information"""
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
