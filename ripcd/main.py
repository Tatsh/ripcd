"""CLI entry point for ripcd."""

from __future__ import annotations

from pathlib import Path
import getpass
import subprocess as sp

from bascom import setup_logging
import click
import requests

from .constants import DEFAULT_DRIVE_SR0
from .rip import rip_cdda_to_flac

__all__ = ('main',)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option(
    '-D',
    '--drive',
    default='/dev/sr0',
    help='Optical drive path.',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    '-M',
    '--accept-first-cddb-match',
    is_flag=True,
    help='Accept the first CDDB match in case of multiple matches.',
)
@click.option('--album-artist', help='Album artist override.')
@click.option('--album-dir', help='Album directory name. Defaults to artist-album-year format.')
@click.option('--cddb-host', help='CDDB host (default from keyring gnudb/<user>).')
@click.option('--never-skip',
              help="Passed to cdparanoia's --never-skip=... option.",
              type=int,
              default=5)
@click.option('-d', '--debug', is_flag=True, help='Enable debug output.')
@click.option('-o',
              '--output-dir',
              help='Parent directory for album_dir. Defaults to current directory.')
@click.option('-u', '--username', default=None, help='Username for CDDB.')
def main(
    drive: Path = DEFAULT_DRIVE_SR0,
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
    """
    Rip an audio disc to FLAC files.

    Requires cdparanoia and flac to be in PATH.

    For Linux only.
    """  # noqa: DOC501
    setup_logging(debug=debug, loggers={'ripcd': {}})
    if username is None:  # pragma: no cover
        username = getpass.getuser()
    try:
        rip_cdda_to_flac(
            drive,
            accept_first_cddb_match=accept_first_cddb_match,
            album_artist=album_artist,
            album_dir=album_dir,
            cddb_host=cddb_host,
            never_skip=never_skip,
            output_dir=output_dir,
            username=username,
        )
    except (sp.CalledProcessError, requests.RequestException, ValueError) as e:
        click.echo(str(e), err=True)
        raise click.Abort from e
