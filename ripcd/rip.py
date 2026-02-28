"""Rip audio CD to FLAC."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
import logging
import subprocess as sp

from deltona.media import cddb_query, get_cd_disc_id

if TYPE_CHECKING:
    from collections.abc import Callable

    from deltona.typing import StrPath

log = logging.getLogger(__name__)


def rip_cdda_to_flac(
    drive: StrPath,
    *,
    accept_first_cddb_match: bool = True,
    album_artist: str | None = None,
    album_dir: StrPath | None = None,
    cddb_host: str | None = None,
    never_skip: int = 5,
    output_dir: StrPath | None = None,
    stderr_callback: Callable[[str], None] | None = None,
    username: str | None = None,
) -> None:
    """
    Rip an audio disc to FLAC files.

    Requires ``cdparanoia`` and ``flac`` to be in ``PATH``.

    Raises
    ------
    CalledProcessError
    """
    result = cddb_query(
        get_cd_disc_id(drive),
        app='ripcd rip_cdda',
        accept_first_match=accept_first_cddb_match,
        host=cddb_host,
        username=username,
    )
    log.debug('Result: %s', result)
    output_dir = Path(output_dir or '.')
    album_dir = ((output_dir / album_dir) if album_dir else output_dir /
                 f'{album_artist or result.artist}-{result.album}-{result.year}')
    album_dir.mkdir(parents=True, exist_ok=True)
    for i, track in enumerate(result.tracks, 1):
        wav = album_dir / f'{i:02d}-{result.artist}-{track}.wav'
        flac = str(wav.with_suffix('.flac'))
        cdparanoia_command = (
            'cdparanoia',
            f'--force-cdrom-device={drive}',
            *(('--quiet', '--stderr-progress') if stderr_callback else ()),
            f'--never-skip={never_skip:d}',
            '--abort-on-skip',
            str(i),
            str(wav),
        )
        proc = sp.Popen(
            cdparanoia_command,
            stderr=sp.PIPE if stderr_callback else None,
            stdout=sp.PIPE if stderr_callback else None,
            text=True,
        )
        if stderr_callback:
            assert proc.stderr is not None
            while proc.stderr.readable():
                if line := proc.stderr.readline().strip():
                    stderr_callback(line)
        log.debug('Waiting for cdparanoia to finish (i = %d, track = "%s").', i, track)
        if (code := proc.wait()) != 0:
            raise sp.CalledProcessError(code, cdparanoia_command)
        sp.run(
            (
                'flac',
                '--delete-input-file',
                '--force',
                '--replay-gain',
                '--silent',
                '--verify',
                f'--output-name={flac}',
                f'--tag=ALBUM={result.album}',
                f'--tag=ALBUMARTIST={album_artist or result.artist}',
                f'--tag=ARTIST={result.artist}',
                f'--tag=GENRE={result.genre}',
                f'--tag=TITLE={track}',
                f'--tag=TRACKNUMBER={i:02d}',
                f'--tag=YEAR={result.year:04d}',
                str(wav),
            ),
            check=True,
        )
