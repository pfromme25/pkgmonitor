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

from pkgmonitor.parser import Parser
from pkgmonitor.fetcher import Fetcher
from pkgmonitor.hash import CacheCheck
from pkgmonitor.terminalhelper import trm
from pkgmonitor.cache import Cache
import argparse
import os
import yaml
import subprocess
import shutil
import pathlib
import configparser

parser = argparse.ArgumentParser(description="Update local Package cache")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-u', '--update', action='store_true', help='Take fetch cache and create package Cache. Checks for hash if fetch cache exists.')
parser.add_argument('-f', '--fetch', action='store_true', help='Fetch repositories into fetch cache. Does not create package Cache')
group.add_argument('-r', '--rebuild', action='store_true', help='Remove all existing cache and rebuild it.')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
args = parser.parse_args()

# Read default config file and set values accordingly
config = configparser.ConfigParser()
config.read('./pkgmonitor.conf.default')
package_cache = config.get('global', 'package_cache')
fetch_cache = config.get('global', 'fetch_cache')
reposd = config.get('pkgmonitor-update', 'repos.d')

# Read user specific config file
if os.path.exists('/etc/pkgmonitor.conf'):
    config.read('/etc/pkgmonitor.conf')
    if config.has_option('global', 'package_cache'):
        package_cache = config.get('global', 'package_cache')
    if config.has_option('global', 'fetch_cache'):
        fetch_cache = config.get('global', 'fetch_cache')
    if config.has_option('pkgmonitor-update', 'repos.d'):
        reposd = config.get('pkgmonitor-update', 'repos.d')

# Create cache helper for removing cache files, getting file paths etc.
cache = Cache(fetch_cache, package_cache, args.verbose)

# Delete the download cache if rebuild option is used.
if args.rebuild:
    if args.verbose:
        print("Removing existing fetch cache")
    cache.delFetchContent()

# Download packages.gz files, if fetch option is used.
if args.fetch:
    for yaml_file in pathlib.Path(reposd).glob('*'):
        if args.verbose:
            print(str(yaml_file))
        with open(str(yaml_file.absolute()), 'r', encoding='latin1') as stream:
            data = yaml.safe_load(stream)
            if data is None:
                if args.verbose:
                    print("File is empty!")
                    print(trm.sep())
            else:
                for repo in data:
                    name = repo['name']
                    if args.verbose:
                        print("Fetching: "+ name)
                    for dists in repo['repository']:
                        url = dists['url']
                        arch = dists['arch']
                        dist = dists['dist']
                        if args.verbose:
                            print("URL: "+url)
                            print("arch: "+str(arch))
                            print("dist: "+str(dist))
                        f = Fetcher(name, dist, url, arch, args.verbose, fetch_cache)
                        f.get_packages()
                    if args.verbose:
                        print(trm.sep())

# Update or rebuild package cache
hash_check_failed = False
if args.update:
    if args.verbose:
        print("Checking Hashes")
    for repo in cache.getFetchHead():
        repo_name = repo[repo.rfind('/')+1:]
        if args.verbose:
            print(repo)
        for f in cache.getFetchContent(repo):
            c = CacheCheck(f)
            if c.check_package_gz():
                if args.verbose:
                    print("MATCH: "+f)
            else:
                if args.verbose:
                    print("FAIL: "+f)
                hash_check_failed = True
        if hash_check_failed:
            if args.verbose:
                print("Rebuilding package cache, removing existing cache")
            cache.delPackageContent(repo_name)
            p = Parser(repo_name, repo, package_cache, args.verbose)
            p.parse()
        hash_check_failed = False
        if args.verbose:
            print(trm.sep())
elif args.rebuild:
    if args.verbose:
        print("Removing existing cache")
    for repo in cache.getPackagesHead():
        repo_name = repo[repo.rfind('/')+1:]
        if args.verbose:
            print(repo_name)
        cache.delPackageContent(repo)
        if args.verbose:
            print(trm.sep())
    for repo in cache.getFetchHead():
        for f in cache.getFetchContent(repo):
            c = CacheCheck(f)
            c.check_package_gz()
        repo_name = repo[repo.rfind('/')+1:]
        if args.verbose:
            print(repo_name)
        p = Parser(repo_name,repo,package_cache,args.verbose)
        p.parse()
        if args.verbose:
            print(trm.sep())
