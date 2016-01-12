# -*- coding: utf-8 -*-


def display(pkgsinfo, overrides_only=False):
    print 'check versions'
    print '--------------'
    pkgs = pkgsinfo['pkgs']
    for pkg in sorted(pkgs):
        if overrides_only and len(pkgs[pkg]) < 2:
            continue
        print pkg.ljust(pkgsinfo['pkg_maxlen'], '.'),
        for idx, name in enumerate(pkgs[pkg]):
            version = pkgs[pkg][name].ljust(pkgsinfo['ver_maxlen'], '.')
            if idx == 0:
                print version + ' ' + name
            else:
                print ' ' * (pkgsinfo['pkg_maxlen'] + 1) + version + ' ' + name
