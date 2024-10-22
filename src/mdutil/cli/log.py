import click


class Logger:
    def __init__(self, is_silent: bool) -> None:
        self.is_silent = is_silent

    def info(self, message: str):
        """Print info messages only when not silent"""
        if not self.is_silent:
            click.echo(message)

    def error(self, message: str):
        """Always print error messages"""
        click.echo(message, err=True)

    def debug(self, message: str):
        if not self.is_silent:
            click.echo(f"DEBUG: {message}")
