"""Console script for trace_poc."""
import os
from shutil import make_archive
import sys
import tempfile
import click
import requests


@click.group()
@click.option("--debug/--no-debug", default=False)
def main(debug):
    """Define main command group."""
    click.echo(f"Debug mode is {'on' if debug else 'off'}")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--direct",
    help="Pass PATH directly instead of creating a zipball out of it.",
    is_flag=True,
)
@click.option(
    "--entrypoint",
    help="Entrypoint that should be used while executing a run.",
    type=str,
    show_default=True,
    default="run.sh",
)
def submit(path, direct, entrypoint):
    """Submit a job to a TRACE system."""
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        click.echo("PATH needs to be a directory")
        return 1
    if direct:
        click.echo(f"{path} will be passed directly")
        with requests.post(
            "http://127.0.0.1:8000",
            params={"entrypoint": entrypoint, "path": path},
            stream=True
        ) as response:
            for line in response.iter_lines(decode_unicode=True):
                print(line)
    else:
        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
            make_archive(tmp.name[:-4], "zip", os.path.abspath(path))
            with requests.post(
                "http://127.0.0.1:8000",
                params={"entrypoint": entrypoint},
                files={"file": ("random.zip", tmp)},
                stream=True,
            ) as response:
                for line in response.iter_lines(decode_unicode=True):
                    print(line)
        click.echo(click.format_filename(os.path.abspath(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
