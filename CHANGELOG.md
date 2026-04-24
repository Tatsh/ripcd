<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.1/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2026-04-24

### Added

- MusicBrainz release metadata lookup before CDDB; CDDB is still queried when MusicBrainz has no
  suitable release or errors occur.

### Changed

- Track extraction and FLAC encoding now run concurrently: `cdparanoia` reads the next track while
  `flac` encodes the previous one, reducing total rip time on multi-track discs.
- Made `rip_cdda_to_flac` asynchronous; await it or run it on an event loop when using the Python
  API (the CLI is unchanged).
- Default `--drive` path now comes from libdiscid when available, otherwise `/dev/sr0`.
- Disc ID read failures raise `ValueError` with a clear message and chained exception.
- When MusicBrainz does not yield metadata and CDDB fails, raises `RuntimeError` with a clear
  message and chained exception.
- Switched the CDDB HTTP client from `requests` to `niquests`.
- Descriptions and CLI help no longer state Linux-only; `cdparanoia` and `flac` are still required
  in `PATH`.

## [0.0.1] - 2026-03-21

### Added

- Initial release as a standalone package (moved from deltona).
- Rip audio CDs to FLAC with CDDB metadata.
- CLI with options for drive path, CDDB host, album artist override, and output directory.

[Unreleased]: https://github.com/Tatsh/ripcd/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/Tatsh/ripcd/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Tatsh/ripcd/releases/tag/v0.0.1
