import click

from engraft import __version__
from engraft.engine import apply


@click.group()
@click.version_option(version=__version__)
def main():
    """engraft - Apply customizations to any project without templating placeholders."""
    pass


@main.command(name="apply")
@click.option(
    "--template",
    required=True,
    type=click.Path(exists=True),
    help="Path to the template YAML file",
)
@click.option(
    "--values",
    required=True,
    type=click.Path(exists=True),
    help="Path to the values YAML file",
)
def apply_cmd(template: str, values: str):
    """Apply a template with values to the current directory."""
    try:
        apply(template, values)
        click.echo("Done. Customizations applied successfully.")
    except FileNotFoundError as e:
        raise click.ClickException(str(e)) from e
    except ValueError as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}") from e
