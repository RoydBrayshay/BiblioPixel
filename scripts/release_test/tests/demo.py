import common


def run():
    common.prompt('Press return to start demo tests')
    for i, demo in enumerate(('bloom', 'circle', 'cube', 'matrix')):
        if i:
            common.execute('bp', 'demo', demo, '--pl=3', '--simpixel=no')
        else:
            common.execute('bp', 'demo', demo, '--pl=3')