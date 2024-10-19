import sys
import traceback
from functools import wraps

import click


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
