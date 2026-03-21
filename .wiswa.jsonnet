local utils = import 'utils.libjsonnet';

{
  description: 'Rip audio CD to FLAC with CDDB metadata.',
  keywords: ['cd', 'cddb', 'flac', 'rip'],
  project_name: 'ripcd',
  version: '0.0.0',
  want_main: true,
  want_man: true,
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          bascom: utils.latestPypiPackageVersionCaret('bascom'),
          click: utils.latestPypiPackageVersionCaret('click'),
          deltona: {
            python: '>=3.11,<3.14',
            version: utils.latestPypiPackageVersionCaret('deltona'),
          },
          requests: utils.latestPypiPackageVersionCaret('requests'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
            },
          },
        },
      },
    },
  },
  copilot: {
    intro: 'ripcd is a simple CLI application to rip a CD to FLAC with CDDB metadata.',
  },
  pyinstaller+: {
    collect_data: ['binaryornot'],
  },
  local apt_packages = ['libcairo2-dev', 'libgirepository-2.0-dev'],
  github+: {
    workflows+: {
      appimage+: {
        apt_packages: apt_packages,
      },
      pyinstaller+: {
        apt_packages: apt_packages,
      },
      qa+: {
        apt_packages: apt_packages,
      },
      tests+: {
        apt_packages: apt_packages,
      },
    },
  },
  snap_python_build_packages: [
    'libcairo2-dev',
    'libgirepository-2.0-dev',
    'pkg-config',
  ],
  readthedocs+: {
    build+: {
      apt_packages: apt_packages,
      os: 'ubuntu-24.04',
    },
  },
}
