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
}
