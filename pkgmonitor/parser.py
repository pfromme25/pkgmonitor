#/usr/bin/python3
# Copyright (C) 2019 Philipp Fromme
#
# This file is part of Pkgmonitor, a tool to locally cache and search through deb repositories.
#
# Pkgmonitor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pkgmonitor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import gzip
import sys
import pathlib
import time

class Parser:
    def __init__(self, name, fetch, cache_dir, verbose=False):
        self.name = name
        self.fetch = [str(fetch) for fetch in pathlib.Path(fetch).glob('*.gz')]
        self.verbose = verbose
        self.pkg_counter = 0
        self.dir = os.path.join(cache_dir, name)
        self.__create_cache()

    def __listdir_fullpath(self, d):
        return [os.path.join(d, f) for f in os.listdir(d)]

    def __create_cache(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def __write_pkg(self, pkg, cache_file):
        if os.path.exists(os.path.join(self.dir, cache_file)):
            open_flag = 'a'
        else:
            open_flag = 'w'
        pkg_file = open(os.path.join(self.dir,cache_file), open_flag)
        pkg_file.write(pkg+'\n')
        pkg_file.close()

    def __interpret_pkg(self, pkg):
        if pkg.startswith('lib'):
            return pkg[0:4]
        else:
            return pkg[0]

    def parse(self):
        for pkggz in self.fetch:
            f = gzip.open(pkggz, mode='rt', encoding="utf-8")
            for line in f:
                if line.startswith('Package:'):
                    self.pkg_counter += 1
                    pkg = line.split()[1]
                    cache_file = self.__interpret_pkg(pkg)
                    self.__write_pkg(pkg, cache_file)
                    if self.verbose:
                        msg = "Writing to file: "+cache_file+" line: "+pkg
                        print('\x1b[2K', end='\r')
                        print(msg, end='\r')
            f.close()
        if self.verbose:
            print()
            print("Parsed "+str(self.pkg_counter)+" packages.")
