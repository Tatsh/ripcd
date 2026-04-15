"""CLI entry point for ripcd."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, cast
import asyncio
import getpass
import subprocess as sp

from bascom import setup_logging
import click
import niquests

from .rip import rip_cdda_to_flac

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ('main',)


def _get_default_drive() -> str:
    try:
        discid = import_module('discid')
    except (ImportError, OSError):
        return '/dev/sr0'
    get_default_device = cast('Callable[[], str]', discid.get_default_device)
    return get_default_device()


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option(
    '-D',
    '--drive',
    default=_get_default_drive,
    help='Optical drive path.',
    show_default='platform default from libdiscid',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    '-M',
    '--accept-first-cddb-match',
    is_flag=True,
    help='Accept the first CDDB match in case of multiple matches.',
)
@click.option('--album-artist', help='Album artist override.')
@click.option('--album-dir', help='Album directory name. Defaults to the artist-album-year format.')
@click.option(
    '--cddb-host',
    help='CDDB host (default is read from the keyring under gnudb/<user>).',
)
@click.option('--never-skip',
              help="Passed to cdparanoia's --never-skip=... option.",
              type=int,
              default=5)
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-o',
              '--output-dir',
              help='Parent directory for album_dir. Defaults to the current directory.')
@click.option('-u', '--username', default=None, help='Username for CDDB.')
def main(
    drive: Path,
    album_artist: str | None = None,
    album_dir: str | None = None,
    cddb_host: str | None = None,
    never_skip: int = 5,
    output_dir: str | None = None,
    username: str | None = None,
    *,
    accept_first_cddb_match: bool = True,
    debug: bool = False,
) -> None:
    """Rip an audio disc to FLAC files; requires cdparanoia and flac in PATH."""  # noqa: DOC501
    setup_logging(debug=debug, loggers={'ripcd': {}})
    if username is None:  # pragma: no cover
        username = getpass.getuser()
    try:
        asyncio.run(
            rip_cdda_to_flac(
                drive,
                accept_first_cddb_match=accept_first_cddb_match,
                album_artist=album_artist,
                album_dir=album_dir,
                cddb_host=cddb_host,
                never_skip=never_skip,
                output_dir=output_dir,
                username=username,
            ))
    except (RuntimeError, sp.CalledProcessError, niquests.RequestException, ValueError) as e:
        click.echo(str(e), err=True)
        raise click.Abort from e
