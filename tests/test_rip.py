"""Tests for rip_cdda_to_flac."""

from __future__ import annotations

from typing import TYPE_CHECKING
import subprocess as sp

from ripcd.rip import rip_cdda_to_flac
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def test_rip_cdda_to_flac_creates_album_dir_and_flac_files(mocker: MockerFixture,
                                                           tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'TestArtist'
    fake_cddb_result.album = 'TestAlbum'
    fake_cddb_result.year = 2023
    fake_cddb_result.tracks = ('Track1', 'Track2')
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mock_run = mocker.patch('ripcd.rip.sp.run')
    mock_popen = mocker.patch('ripcd.rip.sp.Popen')
    mock_popen.return_value.wait.return_value = 0
    album_dir = tmp_path / 'TestArtist-TestAlbum-2023'
    rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, stderr_callback=None, username='user')
    assert album_dir.exists()
    assert mock_popen.call_count == len(fake_cddb_result.tracks)
    assert mock_run.call_count == len(fake_cddb_result.tracks)


def test_rip_cdda_to_flac_album_artist_override(mocker: MockerFixture, tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'WrongArtist'
    fake_cddb_result.album = 'Album'
    fake_cddb_result.year = 2022
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch('ripcd.rip.sp.Popen').return_value.wait.return_value = 0
    mocker.patch('ripcd.rip.sp.run')
    album_dir = tmp_path / 'Override-Album-2022'
    rip_cdda_to_flac(
        drive='/dev/cdrom',
        output_dir=tmp_path,
        album_artist='Override',
        stderr_callback=None,
        username='user',
    )
    assert album_dir.exists()


def test_rip_cdda_to_flac_calls_stderr_callback(mocker: MockerFixture, tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'A'
    fake_cddb_result.album = 'B'
    fake_cddb_result.year = 2021
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch('ripcd.rip.sp.run')
    mock_proc = mocker.Mock()
    mock_proc.stderr = mocker.Mock()
    mock_proc.stderr.readline.side_effect = ['progress line\n', '\n']
    mock_proc.stderr.readable.side_effect = [True, True, False]
    mock_proc.wait.return_value = 0
    mocker.patch('ripcd.rip.sp.Popen', return_value=mock_proc)
    cb = mocker.Mock()
    rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, stderr_callback=cb, username='user')
    cb.assert_any_call('progress line')


def test_rip_cdda_to_flac_raises_on_cdparanoia_failure(mocker: MockerFixture,
                                                       tmp_path: Path) -> None:
    fake_cddb_result = mocker.Mock()
    fake_cddb_result.artist = 'A'
    fake_cddb_result.album = 'B'
    fake_cddb_result.year = 2021
    fake_cddb_result.tracks = ('T1',)
    mocker.patch('ripcd.rip.cddb_query', return_value=fake_cddb_result)
    mocker.patch('ripcd.rip.get_cd_disc_id', return_value='fake_disc_id')
    mocker.patch('ripcd.rip.sp.Popen').return_value.wait.return_value = 1
    with pytest.raises(sp.CalledProcessError):
        rip_cdda_to_flac(drive='/dev/cdrom', output_dir=tmp_path, username='user')
