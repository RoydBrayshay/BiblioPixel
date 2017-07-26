import gitty, json, os
from .. project import project

"""Common command line arguments for run and demo."""


def _get_version():
    from os.path import abspath, dirname, join
    filename = join(dirname(dirname(dirname(abspath(
        __file__)))), 'bibliopixel', 'VERSION')
    return open(filename).read().strip()


COMPONENTS = 'driver', 'layout', 'animation'
PRESET_LIBRARY_DEFAULT = '~/.bibliopixel'
LOG_LEVELS = ('debug', 'info', 'warning', 'error', 'critical')
ENABLE_PRESETS = False

PATH_HELP = """\
A list of directories, separated by colons, 'which are added to the end of
`sys.path`.

You can also use gitty-style paths which start with `//git/` to
dynamically load a library from a public git repository.

See https://github.com/ManiacalLabs/BiblioPixel/wiki/BiblioPixel-Paths
for more information.
"""

LOGLEVEL_HELP = """\
Set what level of events to log. Higher log levels print less."""

VERBOSE_HELP = """\
If this is set, then errors are reported with a full stack trace.
If not set, just the exception message is printed.
"""

VERSION = _get_version()
VERSION_HELP = """\
Print the current version number of BiblioPixel (%s).
""" % VERSION

PRESET_HELP = """Filenames for preset library"""


def add_common_flags(parser):
    parser.add_argument(
        '--loglevel', choices=LOG_LEVELS, default='info', help=LOGLEVEL_HELP)
    parser.add_argument(
        '--verbose', '-v', action='store_true', help=VERBOSE_HELP)
    parser.add_argument(
        '--version', action='store_true', help=VERSION_HELP)
    if ENABLE_PRESETS:
        parser.add_argument(
            '--presets', help=PRESET_HELP, default=PRESET_LIBRARY_DEFAULT)


def add_project_flags(parser):
    parser.add_argument(
        '-a', '--animation', default=None,
        help='Default animation type if no animation is specified')

    parser.add_argument(
        '-d', '--driver', default='simpixel',
        help='Default driver type if no driver is specified')

    parser.add_argument(
        '-l', '--layout', default='matrix',
        help='Default layout class if no layout is specified')

    parser.add_argument(
        '-n', '--numpy', action='store_true',
        help='Use numpy if it available.')

    parser.add_argument(
        '-p', '--path', default=None, help=PATH_HELP)

    parser.add_argument(
        '-s', action='store_true', help='Run SimPixel at the default URL')

    parser.add_argument(
        '--simpixel', help='Run SimPixel at a specific URL')

    parser.add_argument(
        '-t', '--ledtype', default=None,
        help='Default LED type if no LED type is specified')


def make_animation(args, desc):
    def get_value(name):
        value = args and getattr(args, name)
        if not value:
            return {}

        if '{' in value:
            return json.loads(value)

        return {'typename': value}

    project_flags = {name: get_value(name) for name in COMPONENTS}
    if args and args.ledtype:
        project_flags['driver']['ledtype'] = args.ledtype

    if args and args.numpy:
        project_flags['maker'] = {'use_numpy': True}

    return project.project_to_animation(desc, project_flags)


def extend_path(args):
    path = os.getcwd()
    if args.path:
        path += ':' + args.path
    gitty.sys_path.extend(path)