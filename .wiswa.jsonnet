local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Rip audio CDs to FLAC, with metadata.',
  keywords: ['cd', 'cddb', 'flac', 'rip'],
  project_name: 'ripcd',
  version: '0.0.3',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.ripcd' },
  want_man: true,
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          bascom: utils.latestPypiPackageVersionCaret('bascom'),
          click: utils.latestPypiPackageVersionCaret('click'),
          deltona: {
            extras: ['media'],
            version: utils.latestPypiPackageVersionCaret('deltona'),
          },
          discid: utils.latestPypiPackageVersionCaret('discid'),
          musicbrainzngs: utils.latestPypiPackageVersionCaret('musicbrainzngs'),
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          niquests: utils.latestPypiPackageVersionCaret('niquests'),
        },
        group+: {
          tests+: {
            dependencies+: {
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
            },
          },
        },
      },
    },
  },
  github+: {
    workflows+: {
      appimage+: {
        apt_packages: ['libdiscid-dev'],
      },
      codeql+: {
        apt_packages: ['libdiscid-dev'],
      },
      qa+: {
        apt_packages: ['libdiscid-dev'],
      },
      tests+: {
        apt_packages: ['libdiscid-dev'],
      },
    },
  },
  readthedocs+: {
    build+: {
      apt_packages: ['libdiscid-dev'],
    },
  },
  // Required by deltona (transitive dependency: binaryornot).
  pyinstaller+: {
    collect_data: ['binaryornot'],
  },
  snapcraft+: {
    parts+: {
      ripcd+: {
        source: 'https://github.com/Tatsh/ripcd.git',
        'source-tag': 'v0.0.3',
        'source-type': 'git',
      },
    },
  },
  flatpak+: {
    modules: [
      {
        name: 'ripcd',
        buildsystem: 'simple',
        'build-options': { 'build-args': ['--share=network'] },
        'build-commands': [
          'pip3 install --prefix=/app uv',
          '/app/bin/uv pip install --prefix=/app .',
        ],
        sources: [
          {
            type: 'git',
            url: 'https://github.com/Tatsh/ripcd.git',
            tag: 'v0.0.3',
          },
        ],
      },
    ],
  },
}
