# ripcd

[![Python versions](https://img.shields.io/pypi/pyversions/ripcd.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/ripcd)](https://pypi.org/project/ripcd/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/ripcd)](https://github.com/Tatsh/ripcd/tags)
[![License](https://img.shields.io/github/license/Tatsh/ripcd)](https://github.com/Tatsh/ripcd/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/ripcd/v0.0.0/master)](https://github.com/Tatsh/ripcd/compare/v0.0.0...master)
[![CodeQL](https://github.com/Tatsh/ripcd/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tatsh/ripcd/actions/workflows/codeql.yml)
[![QA](https://github.com/Tatsh/ripcd/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/ripcd/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/ripcd/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/ripcd/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/ripcd/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/ripcd?branch=master)
[![Dependabot](https://img.shields.io/badge/Dependabot-enabled-blue?logo=dependabot)](https://github.com/dependabot)
[![Documentation Status](https://readthedocs.org/projects/ripcd/badge/?version=latest)](https://ripcd.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![Poetry](https://img.shields.io/badge/Poetry-242d3e?logo=poetry)](https://python-poetry.org)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3?logo=pydocstyle)](https://www.pydocstyle.org/)
[![pytest](https://img.shields.io/badge/pytest-enabled-CFB97D?logo=pytest)](https://docs.pytest.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/ripcd/month)](https://pepy.tech/project/ripcd)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/ripcd?logo=github&style=flat)](https://github.com/Tatsh/ripcd/stargazers)
[![Prettier](https://img.shields.io/badge/Prettier-enabled-black?logo=prettier)](https://prettier.io/)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor=did%3Aplc%3Auq42idtvuccnmtl57nsucz72&query=%24.followersCount&label=Follow+%40Tatsh&logo=bluesky&style=social)](https://bsky.app/profile/Tatsh.bsky.social)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Tatsh-black?logo=buymeacoffee)](https://buymeacoffee.com/Tatsh)
[![Libera.Chat](https://img.shields.io/badge/Libera.Chat-Tatsh-black?logo=liberadotchat)](irc://irc.libera.chat/Tatsh)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)
[![Patreon](https://img.shields.io/badge/Patreon-Tatsh2-F96854?logo=patreon)](https://www.patreon.com/Tatsh2)

Rip audio CD to FLAC with CDDB metadata. Linux only. Requires `cdparanoia` and `flac` in PATH.

## Installation

```bash
pip install ripcd
```

## Usage

```plain
Usage: ripcd [OPTIONS]

  Rip an audio disc to FLAC files.

  Requires cdparanoia and flac to be in PATH.

  For Linux only.

Options:
  -D, --drive FILE               Optical drive path.
  -M, --accept-first-cddb-match  Accept the first CDDB match in case of
                                 multiple matches.
  --album-artist TEXT            Album artist override.
  --album-dir TEXT               Album directory name. Defaults to artist-
                                 album-year format.
  --cddb-host TEXT               CDDB host (default from keyring
                                 gnudb/<user>).
  --never-skip INTEGER           Passed to cdparanoia's --never-skip=...
                                 option.
  -d, --debug                    Enable debug output.
  -o, --output-dir TEXT          Parent directory for album_dir. Defaults to
                                 current directory.
  -u, --username TEXT            Username for CDDB.
  -h, --help                     Show this message and exit.
```

CDDB host can be set via keyring under the `gnudb` key for your username, or via `--cddb-host`.
