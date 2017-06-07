# -*- coding: utf-8 -*-


class VersionInfo(object):

    def __init__(self, version, source='DEFAULT', annotation=''):
        self.version = version
        self.source = source
        self.annotation = annotation
        self.release_date = None
