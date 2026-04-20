"""Tests for rip_cdda_to_flac."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
import subprocess as sp

from deltona.media import CDDBQueryResult
from ripcd.rip import rip_cdda_to_flac
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def _make_process(*, code: int = 0) -> MagicMock:
    process = MagicMock()
    process.wait = AsyncMock(return_value=code)
    process.stderr = None
    return process


def _musicbrainz_disc_response(
    *,
    artist: str = 'TestArtist',
    album: str = 'TestAlbum',
    year_date: str = '2023',
    track_titles: tuple[str, ...] = ('Track1', 'Track2')) -> dict[str, object]:
    track_list = [{'recording': {'title': t}} for t in track_titles]
    return {
        'disc': {
            'release-list': [{
                'artist-credit-phrase': artist,
                'title': album,
                'date': year_date,
                'medium-list': [{
                    'track-list': track_list
                }]
            }]
        }
    }


@dataclass
class _FakeDisc:
    id: str = 'fake_mb_id'
    cddb_query_string: str = 'fake_cddb_query'


def _make_disc() -> _FakeDisc:
    return _FakeDisc()


def _patch_musicbrainz_success(
    mocker: MockerFixture,
    *,
    artist: str = 'TestArtist',
    album: str = 'TestAlbum',
    year_date: str = '2023',
    track_titles: tuple[str, ...] = ('Track1', 'Track2')) -> None:
    mocker.patch('ripcd.rip.musicbrainzngs.set_useragent')
    mocker.patch('ripcd.rip.musicbrainzngs.get_releases_by_discid',
                 return_value=_musicbrainz_disc_response(artist=artist,
                                                         album=album,
                                                         year_date=year_date,
                                                         track_titles=track_titles))


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_creates_album_dir_and_flac_files(mocker: MockerFixture,
                                                                 tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker)
    cddb_mock = mocker.patch('ripcd.rip.cddb_query')
    mock_create_subprocess = mocker.patch(
        'ripcd.rip.asyncio.create_subprocess_exec',
        side_effect=[_make_process(),
                     _make_process(),
                     _make_process(),
                     _make_process()])
    album_dir = tmp_path / 'TestArtist-TestAlbum-2023'
    await rip_cdda_to_flac(drive='/dev/cdrom',
                           output_dir=tmp_path,
                           stderr_callback=None,
                           username='user')
    assert album_dir.exists()
    assert mock_create_subprocess.call_count == 4
    cddb_mock.assert_not_called()


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_starts_next_rip_after_flac_starts(mocker: MockerFixture,
                                                                  tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker)
    mocker.patch('ripcd.rip.cddb_query')
    mock_create_subprocess = mocker.patch(
        'ripcd.rip.asyncio.create_subprocess_exec',
        side_effect=[_make_process(),
                     _make_process(),
                     _make_process(),
                     _make_process()])
    await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')
    commands = [call.args[0] for call in mock_create_subprocess.call_args_list]
    assert commands == ['cdparanoia', 'flac', 'cdparanoia', 'flac']


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_album_artist_override(mocker: MockerFixture,
                                                      tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker,
                               artist='WrongArtist',
                               album='Album',
                               track_titles=('T1',),
                               year_date='2022')
    mocker.patch('ripcd.rip.cddb_query')
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec',
                 side_effect=[_make_process(), _make_process()])
    album_dir = tmp_path / 'Override-Album-2022'
    await rip_cdda_to_flac(drive='/dev/cdrom',
                           output_dir=tmp_path,
                           album_artist='Override',
                           stderr_callback=None,
                           username='user')
    assert album_dir.exists()


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_calls_stderr_callback(mocker: MockerFixture,
                                                      tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker,
                               artist='A',
                               album='B',
                               track_titles=('T1',),
                               year_date='2021')
    mocker.patch('ripcd.rip.cddb_query')
    cdparanoia_process = _make_process()
    cdparanoia_process.stderr = mocker.Mock()
    cdparanoia_process.stderr.readline = AsyncMock(side_effect=[b'progress line\n', b'\n', b''])
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec',
                 side_effect=[cdparanoia_process, _make_process()])
    cb = mocker.Mock()
    await rip_cdda_to_flac(drive='/dev/cdrom',
                           output_dir=tmp_path,
                           stderr_callback=cb,
                           username='user')
    cb.assert_any_call('progress line')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_stderr_none(mocker: MockerFixture,
                                                      tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker,
                               artist='A',
                               album='B',
                               track_titles=('T1',),
                               year_date='2021')
    mocker.patch('ripcd.rip.cddb_query')
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec', return_value=_make_process())
    with pytest.raises(TypeError, match='stderr is None'):
        await rip_cdda_to_flac(drive='/dev/cdrom',
                               output_dir=tmp_path,
                               stderr_callback=mocker.Mock(),
                               username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_cdparanoia_failure(mocker: MockerFixture,
                                                             tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker,
                               artist='A',
                               album='B',
                               track_titles=('T1',),
                               year_date='2021')
    mocker.patch('ripcd.rip.cddb_query')
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec', return_value=_make_process(code=1))
    with pytest.raises(sp.CalledProcessError):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_falls_back_to_cddb(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    mocker.patch('ripcd.rip.musicbrainzngs.set_useragent')
    mocker.patch('ripcd.rip.musicbrainzngs.get_releases_by_discid',
                 return_value={'disc': {
                     'release-list': []
                 }})
    cddb_result = CDDBQueryResult(artist='CddbArtist',
                                  album='CddbAlbum',
                                  year=2020,
                                  genre='Rock',
                                  tracks=('T1',))
    cddb_mock = mocker.patch('ripcd.rip.cddb_query', return_value=cddb_result)
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec',
                 side_effect=[_make_process(), _make_process()])
    await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')
    cddb_mock.assert_called_once_with('fake_cddb_query',
                                      accept_first_match=True,
                                      app='ripcd rip_cdda',
                                      host=None,
                                      username='user')


@pytest.mark.parametrize('accept_first', [True, False])
@pytest.mark.asyncio
async def test_rip_cdda_to_flac_cddb_fallback_honours_accept_first(mocker: MockerFixture,
                                                                   tmp_path: Path, *,
                                                                   accept_first: bool) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    mocker.patch('ripcd.rip.musicbrainzngs.set_useragent')
    mocker.patch('ripcd.rip.musicbrainzngs.get_releases_by_discid',
                 return_value={'disc': {
                     'release-list': []
                 }})
    cddb_result = CDDBQueryResult(artist='A', album='B', year=2000, genre='g', tracks=('t',))
    cddb_mock = mocker.patch('ripcd.rip.cddb_query', return_value=cddb_result)
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec',
                 side_effect=[_make_process(), _make_process()])
    await rip_cdda_to_flac(drive='/dev/cdrom',
                           output_dir=tmp_path,
                           username='u',
                           accept_first_cddb_match=accept_first)
    assert cddb_mock.call_args.kwargs['accept_first_match'] is accept_first


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_musicbrainz_exception_falls_back_to_cddb(
        mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    mocker.patch('ripcd.rip.musicbrainzngs.set_useragent')
    mocker.patch('ripcd.rip.musicbrainzngs.get_releases_by_discid',
                 side_effect=ConnectionError('unreachable'))
    cddb_result = CDDBQueryResult(artist='X', album='Y', year=1999, genre='Pop', tracks=('One',))
    cddb_mock = mocker.patch('ripcd.rip.cddb_query', return_value=cddb_result)
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec',
                 side_effect=[_make_process(), _make_process()])
    await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')
    cddb_mock.assert_called_once()


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_metadata_failure(mocker: MockerFixture,
                                                           tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    mocker.patch('ripcd.rip.musicbrainzngs.set_useragent')
    mocker.patch('ripcd.rip.musicbrainzngs.get_releases_by_discid',
                 return_value={'disc': {
                     'release-list': []
                 }})
    mocker.patch('ripcd.rip.cddb_query', side_effect=RuntimeError('network down'))
    with pytest.raises(RuntimeError, match=r'Failed to query metadata from MusicBrainz and CDDB\.'):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_disc_id_failure(mocker: MockerFixture,
                                                          tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', side_effect=OSError('no medium found'))
    with pytest.raises(ValueError, match=r'Failed to read disc ID\.'):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_flac_failure(mocker: MockerFixture,
                                                       tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.discid.read', return_value=_make_disc())
    _patch_musicbrainz_success(mocker,
                               artist='A',
                               album='B',
                               track_titles=('T1',),
                               year_date='2021')
    mocker.patch('ripcd.rip.cddb_query')
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec',
                 side_effect=[_make_process(), _make_process(code=1)])
    with pytest.raises(sp.CalledProcessError):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')
