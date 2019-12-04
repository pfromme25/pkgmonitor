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
import pathlib

class Cache:
    def __init__(self, fetch_dir, package_dir, verbose):
        self.fetch_dir = fetch_dir
        self.package_dir = package_dir
        self.verbose = verbose
    
    def __getDir(self, directory):
        """Returns the directoy contents
        Args:
            directory: directory to return the contents of
        Returns:
            List of absolute file paths of the specified directory
        """
        file_list = []
        for f in pathlib.Path(directory).glob('*'):
            file_list.append(str(f.absolute()))
        return file_list

    def getFetchHead(self):
        """Returns the file paths of the fetch cache
        Returns:
            List of fetch cache (absolute file path) directories. Parent directories only
        """
        return self.__getDir(self.fetch_dir)

    def getFetchContent(self, directory):
        """Returns the fetch cache contents of a specific repository
        Args:
            directory: Either an absolute file path or the name of the fetch repository
        Returns:
            List of absolute file paths of the fetch repository, excluding any .sha256 files
        """
        if not os.path.isabs(directory):
            content = os.path.join(self.fetch_dir, directory)
        content = self.__getDir(directory)
        clean_content = []
        for f in content:
            if not f.endswith('.sha256'):
                clean_content.append(f)
        return clean_content

    def delFetchContent(self):
        """Deletes every fetch repository
        """
        head = self.getFetchHead()
        for repo in head:
            content = self.__getDir(repo)
            for f in content:
                if self.verbose:
                    print('Removing file: '+f)
                os.remove(f)
            if self.verbose:
                print('Removing dir: '+repo)   
            os.rmdir(repo)

    def getPackagesHead(self):
        """Returns the file paths of the package cache
        Returns:
            List of package cache (absolute file path) directories. Parent directories only
        """
        return self.__getDir(self.package_dir)

    def getPackagesContent(self, directory):
        """Returns the package cache contents of a specific repository
        Args:
            directory: Either an absolute file path or the name of the package repository
        Returns:
            List of absolute file paths of the package repository
        """
        if not os.path.isabs(directory):
            directory = os.path.join(self.package_dir, directory)
        return self.__getDir(directory)

    def delPackageContent(self, directory):
        """Deletes the package cache contents of a specific repository
        Args:
            directory: Either an absolute file path or the name of the package repository
        Returns:
            Nothing
        """
        if not os.path.isabs(directory):
            directory = os.path.join(self.package_dir, directory)
        if os.path.exists(directory):
            for f in self.__getDir(directory):
                if self.verbose:
                    print('Removing file: '+f)
                os.remove(f)
            if self.verbose:
                print('Removing dir: '+directory)   
            os.rmdir(directory)
        else:
            if self.verbose:
                print(directory+" does not exist. Nothing to delete.")
