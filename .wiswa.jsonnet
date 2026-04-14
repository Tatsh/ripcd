local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Rip an audio CD to FLAC with CDDB metadata.',
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
            python: '>=3.11,<3.14',
            version: utils.latestPypiPackageVersionCaret('deltona'),
          },
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          niquests: utils.latestPypiPackageVersionCaret('niquests'),
        },
        group+: {
          dev+: {
            dependencies+: {},
          },
          tests+: {
            dependencies+: {
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
            },
          },
        },
      },
    },
  },
  // Required by deltona (transitive dependency: binaryornot).
  pyinstaller+: {
    collect_data: ['binaryornot'],
  },
}
