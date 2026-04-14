"""CLI tests for ripcd."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
import subprocess as sp

from ripcd.main import main as ripcd
import niquests

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
    mocker.patch(
        'ripcd.main.rip_cdda_to_flac',
        new_callable=AsyncMock,
        side_effect=sp.CalledProcessError(1, ('cdparanoia',)),
    )
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code != 0


def test_ripcd_niquests_request_exception(mocker: MockerFixture, runner: CliRunner,
                                          tmp_path: Path) -> None:
    mocker.patch(
        'ripcd.main.rip_cdda_to_flac',
        new_callable=AsyncMock,
        side_effect=niquests.RequestException('connection failed'),
    )
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code != 0
