"""Tests for rip_cdda_to_flac."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
import subprocess as sp

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


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_creates_album_dir_and_flac_files(mocker: MockerFixture,
                                                                 tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'TestArtist'
    fake_cddb_result.album = 'TestAlbum'
    fake_cddb_result.year = 2023
    fake_cddb_result.tracks = ('Track1', 'Track2')
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mock_create_subprocess = mocker.patch(
        'ripcd.rip.asyncio.create_subprocess_exec',
        side_effect=[
            _make_process(),
            _make_process(),
            _make_process(),
            _make_process(),
        ],
    )
    album_dir = tmp_path / 'TestArtist-TestAlbum-2023'
    await rip_cdda_to_flac(
        drive='/dev/cdrom',
        output_dir=tmp_path,
        stderr_callback=None,
        username='user',
    )
    assert album_dir.exists()
    assert mock_create_subprocess.call_count == len(fake_cddb_result.tracks) * 2


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_album_artist_override(mocker: MockerFixture,
                                                      tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'WrongArtist'
    fake_cddb_result.album = 'Album'
    fake_cddb_result.year = 2022
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch(
        'ripcd.rip.asyncio.create_subprocess_exec',
        side_effect=[_make_process(), _make_process()],
    )
    album_dir = tmp_path / 'Override-Album-2022'
    await rip_cdda_to_flac(
        drive='/dev/cdrom',
        output_dir=tmp_path,
        album_artist='Override',
        stderr_callback=None,
        username='user',
    )
    assert album_dir.exists()


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_calls_stderr_callback(mocker: MockerFixture,
                                                      tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'A'
    fake_cddb_result.album = 'B'
    fake_cddb_result.year = 2021
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    cdparanoia_process = _make_process()
    cdparanoia_process.stderr = mocker.Mock()
    cdparanoia_process.stderr.readline = AsyncMock(side_effect=[b'progress line\n', b'\n', b''])
    mocker.patch(
        'ripcd.rip.asyncio.create_subprocess_exec',
        side_effect=[cdparanoia_process, _make_process()],
    )
    cb = mocker.Mock()
    await rip_cdda_to_flac(
        drive='/dev/cdrom',
        output_dir=tmp_path,
        stderr_callback=cb,
        username='user',
    )
    cb.assert_any_call('progress line')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_stderr_none(mocker: MockerFixture,
                                                      tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'A'
    fake_cddb_result.album = 'B'
    fake_cddb_result.year = 2021
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec', return_value=_make_process())
    with pytest.raises(TypeError, match='stderr is None'):
        await rip_cdda_to_flac(drive='/dev/cdrom',
                               output_dir=tmp_path,
                               stderr_callback=mocker.Mock(),
                               username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_cdparanoia_failure(mocker: MockerFixture,
                                                             tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'A'
    fake_cddb_result.album = 'B'
    fake_cddb_result.year = 2021
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch('ripcd.rip.asyncio.create_subprocess_exec', return_value=_make_process(code=1))
    with pytest.raises(sp.CalledProcessError):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_cddb_failure(mocker: MockerFixture,
                                                       tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch('ripcd.rip.cddb_query', side_effect=RuntimeError('network down'))
    with pytest.raises(ValueError, match=r'Failed to query CDDB\.'):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_disc_id_failure(mocker: MockerFixture,
                                                          tmp_path: Path) -> None:
    mocker.patch('ripcd.rip.get_cd_disc_id', side_effect=OSError('no medium found'))
    with pytest.raises(ValueError, match=r'Failed to query CDDB\.'):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')


@pytest.mark.asyncio
async def test_rip_cdda_to_flac_raises_on_flac_failure(mocker: MockerFixture,
                                                       tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'A'
    fake_cddb_result.album = 'B'
    fake_cddb_result.year = 2021
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch(
        'ripcd.rip.asyncio.create_subprocess_exec',
        side_effect=[_make_process(), _make_process(code=1)],
    )
    with pytest.raises(sp.CalledProcessError):
        await rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')
