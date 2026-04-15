"""Rip an audio CD to FLAC."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, NamedTuple, Protocol, cast
import asyncio
import logging
import subprocess as sp

from deltona.media import cddb_query
import anyio
import discid  # type: ignore[import-untyped]  # Third-party package does not ship typing metadata.
import musicbrainzngs  # type: ignore[import-untyped]  # Third-party package does not ship stubs.

if TYPE_CHECKING:
    from deltona.typing import StrPath

log = logging.getLogger(__name__)


class _AlbumMetadata(NamedTuple):
    artist: str
    album: str
    year: int
    genre: str
    tracks: tuple[str, ...]


class _Disc(Protocol):
    id: str
    cddb_query_string: str


def _coerce_year(value: int | str | None) -> int:
    match value:
        case int():
            return value
        case str():
            return int(value[:4]) if value[:4].isdigit() else 0
        case _:
            return 0


def _extract_track_titles(release: Mapping[str, object]) -> tuple[str, ...]:
    tracks: list[str] = []
    medium_list = release.get('medium-list')
    if not isinstance(medium_list, list):
        return ()
    for medium in medium_list:
        if not isinstance(medium, dict):
            continue
        medium_map = cast('dict[str, object]', medium)
        track_list = medium_map.get('track-list')
        if not isinstance(track_list, list):
            continue
        for track in track_list:
            if not isinstance(track, dict):
                continue
            track_map = cast('dict[str, object]', track)
            recording = track_map.get('recording')
            if isinstance(recording, dict):
                recording_map = cast('dict[str, object]', recording)
            else:
                recording_map = None
            if recording_map is not None and isinstance((title := recording_map.get('title')), str):
                tracks.append(title)
                continue
            if isinstance((title := track_map.get('title')), str):
                tracks.append(title)
    return tuple(tracks)


def _query_musicbrainz(disc_id: str) -> _AlbumMetadata | None:
    try:
        musicbrainzngs.set_useragent('ripcd', '0.0.1', 'https://github.com/Tatsh/ripcd')
        mb_result = musicbrainzngs.get_releases_by_discid(
            disc_id, includes=['artists', 'recordings', 'release-groups', 'tags'])
    except Exception:
        log.debug('MusicBrainz lookup failed for `%s`.', disc_id, exc_info=True)
        return None
    disc_data = mb_result.get('disc')
    if not isinstance(disc_data, Mapping):
        return None
    release_list = disc_data.get('release-list')
    if not isinstance(release_list, list) or not release_list:
        return None
    release = release_list[0]
    if not isinstance(release, Mapping):
        return None
    tracks = _extract_track_titles(release)
    if not tracks:
        return None
    artist = release.get('artist-credit-phrase')
    if not isinstance(artist, str):
        artist = 'Unknown Artist'
    album = release.get('title')
    if not isinstance(album, str):
        album = 'Unknown Album'
    year = _coerce_year(release.get('date'))
    genre = 'Unknown'
    tag_list = release.get('tag-list')
    if isinstance(tag_list, list) and tag_list and isinstance(tag_list[0], dict):
        first_name = cast('dict[str, object]', tag_list[0]).get('name')
        if isinstance(first_name, str) and first_name:
            genre = first_name
    return _AlbumMetadata(artist=artist, album=album, year=year, genre=genre, tracks=tracks)


def _read_disc(drive: StrPath) -> _Disc:
    read_disc = cast('Callable[[str], _Disc]', discid.read)
    return read_disc(str(drive))


def _query_cddb(
    *,
    accept_first_cddb_match: bool,
    cddb_host: str | None,
    cddb_query_string: str,
    username: str | None,
) -> _AlbumMetadata:
    result = cddb_query(
        cddb_query_string,
        app='ripcd rip_cdda',
        accept_first_match=accept_first_cddb_match,
        host=cddb_host,
        username=username,
    )
    return _AlbumMetadata(
        artist=result.artist,
        album=result.album,
        year=result.year,
        genre=result.genre,
        tracks=tuple(result.tracks),
    )


async def _read_progress_stderr(stderr: asyncio.StreamReader,
                                stderr_callback: Callable[[str], None]) -> None:
    while line := await stderr.readline():
        if line_text := line.decode().strip():
            stderr_callback(line_text)


async def _wait_for_process(
    process: asyncio.subprocess.Process,
    command: tuple[str, ...],
    stderr_callback: Callable[[str], None] | None = None,
) -> None:
    if stderr_callback is None:
        code = await process.wait()
    else:
        if process.stderr is None:
            msg = 'stderr is None.'
            raise TypeError(msg)
        _, code = await asyncio.gather(_read_progress_stderr(process.stderr, stderr_callback),
                                       process.wait())
    if code != 0:
        raise sp.CalledProcessError(code, command)


async def rip_cdda_to_flac(
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

    Parameters
    ----------
    drive : StrPath
        Optical drive device path.
    accept_first_cddb_match : bool
        Accept the first CDDB match in case of multiple matches.
    album_artist : str | None
        Album artist override.
    album_dir : StrPath | None
        Album directory name. Defaults to the artist-album-year format.
    cddb_host : str | None
        CDDB host.
    never_skip : int
        Passed to ``cdparanoia``'s ``--never-skip`` option.
    output_dir : StrPath | None
        Parent directory for *album_dir*. Defaults to the current directory.
    stderr_callback : Callable[[str], None] | None
        Callback invoked with each non-empty line from ``cdparanoia``'s standard error.
    username : str | None
        Username for CDDB.

    Raises
    ------
    ValueError
        If reading the disc ID fails.
    RuntimeError
        If metadata lookup from MusicBrainz and CDDB fails.
    subprocess.CalledProcessError
        If ``cdparanoia`` or ``flac`` exits with a non-zero code.
    TypeError
        If stderr is ``None`` when *stderr_callback* is provided.
    """  # noqa: DOC502
    try:
        disc = await asyncio.to_thread(_read_disc, drive)
    except Exception as e:
        msg = 'Failed to read disc ID.'
        raise ValueError(msg) from e
    result = await asyncio.to_thread(_query_musicbrainz, disc.id)
    if result is None:
        try:
            result = await asyncio.to_thread(
                _query_cddb,
                accept_first_cddb_match=accept_first_cddb_match,
                cddb_host=cddb_host,
                cddb_query_string=disc.cddb_query_string,
                username=username,
            )
        except Exception as e:
            msg = 'Failed to query metadata from MusicBrainz and CDDB.'
            raise RuntimeError(msg) from e
    log.debug('Result: %s', result)
    output_dir_path = anyio.Path(output_dir or '.')
    album_dir_path = ((output_dir_path / str(album_dir)) if album_dir else output_dir_path /
                      f'{album_artist or result.artist}-{result.album}-{result.year}')
    await album_dir_path.mkdir(parents=True, exist_ok=True)
    for i, track in enumerate(result.tracks, 1):
        wav_path = album_dir_path / f'{i:02d}-{result.artist}-{track}.wav'
        flac_path = wav_path.with_suffix('.flac')
        cdparanoia_command = (
            'cdparanoia',
            f'--force-cdrom-device={drive}',
            *(('--quiet', '--stderr-progress') if stderr_callback else ()),
            f'--never-skip={never_skip:d}',
            '--abort-on-skip',
            str(i),
            str(wav_path),
        )
        cdparanoia_process = await asyncio.create_subprocess_exec(
            *cdparanoia_command,
            stderr=asyncio.subprocess.PIPE if stderr_callback else None,
            stdout=asyncio.subprocess.DEVNULL if stderr_callback else None,
        )
        log.debug('Waiting for cdparanoia to finish (i = %d, track = "%s").', i, track)
        await _wait_for_process(cdparanoia_process, cdparanoia_command, stderr_callback)
        flac_command = (
            'flac',
            '--delete-input-file',
            '--force',
            '--replay-gain',
            '--silent',
            '--verify',
            f'--output-name={flac_path!s}',
            f'--tag=ALBUM={result.album}',
            f'--tag=ALBUMARTIST={album_artist or result.artist}',
            f'--tag=ARTIST={result.artist}',
            f'--tag=GENRE={result.genre}',
            f'--tag=TITLE={track}',
            f'--tag=TRACKNUMBER={i:02d}',
            f'--tag=YEAR={result.year:04d}',
            str(wav_path),
        )
        flac_process = await asyncio.create_subprocess_exec(*flac_command)
        await _wait_for_process(flac_process, flac_command)
