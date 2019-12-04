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

import hashlib
import os

class CacheCheck:
    def __init__(self, package_gz):
        self.package_gz = package_gz
        self.package_hash_file = self.package_gz + ".sha256"
        self.sha256 = hashlib.sha256()
        self.BUF_SIZE = 65536
        self.__get_hash()

    def __get_hash(self):
        """Sets its own hash value
        """
        with open(self.package_gz, 'rb') as f:
            while True:
                data = f.read(self.BUF_SIZE)
                if not data:
                    break
                self.sha256.update(data)

    def __create_hash_file(self):
        """Caches its own hash value
        """
        hash_file = open(self.package_hash_file, 'w')
        hash_file.write(self.sha256.hexdigest())
        hash_file.close()

    def check_package_gz(self):
        """Compares its own hash value to the cache
        Returns:
            True, if the cached hash value matches its own
            False, if no cached hash exists or the hash does not match
        """
        if os.path.exists(self.package_hash_file):
            pkg_gz = open(self.package_hash_file)
            with open(self.package_hash_file, 'r') as f:
                cache_hash = f.readline()
            if cache_hash == self.sha256.hexdigest():
                return True
            else:
                self.__create_hash_file()
                return False
        else:
            self.__create_hash_file()
            return False

