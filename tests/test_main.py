"""CLI tests for ripcd."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ripcd.main import main as ripcd

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def test_ripcd_success(mocker: MockerFixture, runner: CliRunner, tmp_path: Path) -> None:
    mocker.patch('ripcd.main.rip_cdda_to_flac')
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code == 0


def test_ripcd_error(mocker: MockerFixture, runner: CliRunner, tmp_path: Path) -> None:
    mocker.patch('ripcd.main.rip_cdda_to_flac', side_effect=ValueError('fail'))
    drive_path = tmp_path / 'drive'
    drive_path.touch()
    result = runner.invoke(ripcd, ['--drive', str(drive_path)])
    assert result.exit_code != 0
