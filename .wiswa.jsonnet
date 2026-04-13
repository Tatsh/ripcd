local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Rip audio CD to FLAC with CDDB metadata.',
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
  // Required by deltona (transitive dependency: binaryornot).
  pyinstaller+: {
    collect_data: ['binaryornot'],
  },
}
