#!/usr/bin/python3
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
import yaml
import subprocess

class Fetcher:
    def __init__(self, name, repo, url, arch, verbose, cache):
        self.cache = cache
        self.name = name
        self.repo = repo
        self.url = url
        self.arch = arch
        self.verbose = verbose
        self.dir = os.path.join(self.cache, self.name)
        self.urls_to_fetch = []
        self.__create_cache()
        self.__set_urls()

    def __create_cache(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def __set_urls(self):
        for repo in self.repo:
            for arch in self.arch:
                self.urls_to_fetch.append(self.url.replace('{dist}', repo).replace('{arch}', arch))

    def get_packages(self):
        for url in self.urls_to_fetch:
            filename = url.replace('/', '_')
            if self.verbose:
                print("Fetching: "+url)
            subprocess.run(['wget', url, '--quiet', '-O', os.path.join(self.dir, filename)])
