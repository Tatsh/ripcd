local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Rip audio CDs to FLAC, with metadata.',
  keywords: ['cd', 'cddb', 'flac', 'rip'],
  project_name: 'ripcd',
  version: '0.0.1',
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
}
