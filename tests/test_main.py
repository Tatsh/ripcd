"""CLI tests for ripcd."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
import subprocess as sp

from ripcd.main import main as ripcd
import niquests
import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_ripcd_success(mocker: MockerFixture, runner: CliRunner, tmp_path: Path) -> None:
    mocker.patch('ripcd.main.rip_cdda_to_flac', new_callable=AsyncMock)
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code == 0


def test_ripcd_error(mocker: MockerFixture, runner: CliRunner, tmp_path: Path) -> None:
    mocker.patch('ripcd.main.rip_cdda_to_flac',
                 new_callable=AsyncMock,
                 side_effect=ValueError('fail'))
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code != 0


def test_ripcd_called_process_error(mocker: MockerFixture, runner: CliRunner,
                                    tmp_path: Path) -> None:
    mocker.patch('ripcd.main.rip_cdda_to_flac',
                 new_callable=AsyncMock,
                 side_effect=sp.CalledProcessError(1, ('cdparanoia',)))
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code != 0


def test_ripcd_niquests_request_exception(mocker: MockerFixture, runner: CliRunner,
                                          tmp_path: Path) -> None:
    mocker.patch('ripcd.main.rip_cdda_to_flac',
                 new_callable=AsyncMock,
                 side_effect=niquests.RequestException('connection failed'))
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code != 0


def test_ripcd_help_mentions_drive_default_and_cddb_host(runner: CliRunner) -> None:
    result = runner.invoke(ripcd, ['--help'])
    assert result.exit_code == 0
    out = result.output.replace('\n', ' ')
    assert 'default from libdiscid' in out
    assert 'gnudb' in result.output


@pytest.mark.parametrize(('extra_args', 'expected_accept_first'), [
    pytest.param([], False, id='default_off'),
    pytest.param(['-M'], True, id='short_flag'),
    pytest.param(['--accept-first-cddb-match'], True, id='long_flag')
])
def test_ripcd_accept_first_cddb_match_flag(mocker: MockerFixture, runner: CliRunner,
                                            tmp_path: Path, *, extra_args: list[str],
                                            expected_accept_first: bool) -> None:
    mock_rip = mocker.patch('ripcd.main.rip_cdda_to_flac', new_callable=AsyncMock)
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    args = [*extra_args, '--drive', str(drive_path)]
    result = runner.invoke(ripcd, args)
    assert result.exit_code == 0
    mock_rip.assert_awaited_once()
    assert mock_rip.await_args is not None
    assert mock_rip.await_args.kwargs['accept_first_cddb_match'] is expected_accept_first


def test_ripcd_defaults_never_skip_and_username(mocker: MockerFixture, runner: CliRunner,
                                                tmp_path: Path) -> None:
    mock_rip = mocker.patch('ripcd.main.rip_cdda_to_flac', new_callable=AsyncMock)
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code == 0
    mock_rip.assert_awaited_once()
    assert mock_rip.await_args is not None
    kwargs = mock_rip.await_args.kwargs
    assert kwargs['never_skip'] == 5
    assert kwargs['username'] is not None
