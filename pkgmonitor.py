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
import argparse
import sys
import yaml
import pathlib
import re
import prettytable
import configparser
from prettytable import PrettyTable
from colorama import Fore, Back, Style
from pkgmonitor.terminalhelper import trm
from collections import OrderedDict

parser = argparse.ArgumentParser(description="Check local build repository cache for existing/missing packages")
repo_group = parser.add_mutually_exclusive_group(required=True)
repo_group.add_argument("-a", "--all", help="Check all repos in cache", action="store_true")
repo_group.add_argument("-r", "--repo", nargs='+', type=str, help="Check if packages are (not) found in specified repo")
parser.add_argument("-o", "--ok", help="Output packages that are available", action="store_true")
parser.add_argument("-m", "--missing", help="Output packages that are missing.", action="store_true")
parser.add_argument("-c", "--color", help="Output with color", action="store_true")
indent_group = parser.add_mutually_exclusive_group(required=False)
indent_group.add_argument("-t", "--table", help="Output as table.", action="store_true")
indent_group.add_argument("-i", "--indent", help="Indented output", action="store_true")
parser.add_argument("-f", "--file", nargs='+', type=str, help="Read packages from file")
parser.add_argument("-p", "--packages", nargs='+', type=str, help="Read packages from argument list, divided by space")
parser.add_argument("-v", "--verbose", help="Verbose output, otherwise only return status.", action="store_true")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('./pkgmonitor.conf.default')
release_order = config.get('pkgmonitor', 'release_order')
release_order = release_order.split()
rules_dir = config.get('pkgmonitor', 'rules.d')
package_cache = config.get('global', 'package_cache')

if os.path.exists('/etc/pkgmonitor.conf'):
    config.read('/etc/pkgmonitor.conf')
    if config.has_option('pkgmonitor', 'release_order'):
        release_order = config.get('pkgmonitor', 'release_order')
        release_order = release_order.split()
    if config.has_option('pkgmonitor', 'rules.d'):
        rules_dir = config.get('pkgmonitor', 'rules.d')
    if config.has_option('global', 'package_cache'):
        package_cache = config.get('global', 'package_cache')

def check(repo, pkg_file, pkg):
    with open(os.path.join(repo, pkg_file), 'r') as f:
        for line in f.readlines():
            if line.rstrip() == package:
                return True
        return False

def color_print(string, color):
    if color == None:
        print(string)
    else:
        print(color + string)
        print(Style.RESET_ALL, end='')

def blacklist_regex(blacklist, package):
    for key in blacklist:
        pattern = re.compile(key)
        if pattern.match(package):
            if args.verbose:
                print(package, key)
            return True
    return False

def rename_regex(renamelist, package):
    for dictionary in renamelist:
        for key in dictionary:
            pattern = re.compile(key)
            if pattern.match(package):
                new_name = re.sub(pattern, dictionary[key], package)
                if args.verbose:
                    print(package, key, new_name)
                return new_name
    return None

def filter_package(package):
    removed = False
    package_name = package
    for repo in repo_list:
        for rule_file in rules:
            if repo in rules[rule_file]:
                if type(rules[rule_file][repo][0]) is dict:
                    package_name_tmp = rename_regex(rules[rule_file][repo], package_name)
                    if package_name_tmp is not None:
                        package_name = package_name_tmp
                        package_name_tmp = None
                else:
                    removed = blacklist_regex(rules[rule_file][repo], package_name)
        if not removed:
            packages[repo].append(package_name)
        package_name = package
        removed = False

def print_packages(dict, styling, color):
    for repo in verdict_dict:
        if args.ok:
            for package in verdict_dict[repo]['ok']:
                color_print(styling+package, color)
        if args.missing:
            for package in verdict_dict[repo]['miss']:
                color_print(styling+package,color)

# Build list of repos for -a/--all argument.
repo_list = []
if args.all:
    for repo in os.listdir(package_cache):
        repo_list.append(repo)
else:
    repo_list = args.repo

# Create list to later add packages for each repo specified.
packages = {}
for repo in repo_list:
    packages[repo] = []

# Order repos in repo_list
tmp_repo_list = []
for repo in release_order:
    if repo in repo_list:
        tmp_repo_list.append(repo)
repo_list = tmp_repo_list

# Gather all available rule files in list an sort them to adhere to predictability
rule_files = []
for f in pathlib.Path(rules_dir).glob('*'):
    rule_files.append(str(f.absolute()))
rule_files.sort()

rules = {}
for rfile in rule_files:
    name = rfile[repo.rfind('/')+1:]
    rules[name] = {}
    with open(rfile, 'r', encoding='latin1') as stream:
        data = yaml.safe_load(stream)
        if not data is None:
            for rule in data:
                rules[name][rule['repo']] = rule['packages']
rules = OrderedDict(sorted(rules.items()))

# Use file, arguments or stdin for package names, exit with error if none is used.
no_input = True
if args.file:
    no_input = False
    for pkg_file in args.file:
        with open(pkg_file, 'r') as f:
            for line in f.readlines():
                filter_package(line.rstrip())
if args.packages:
    no_input = False
    for package in args.packages:
        filter_package(package)
if not sys.stdin.isatty():
    no_input = False
    for line in sys.stdin:
        filter_package(line.rstrip())
if no_input:
    sys.exit("No input was given, you need to use -f/--file, -p/--packages or pipe your input to this script.")

# If using table output, save all packages in a list without repo specification
# Otherwise, remove all redundancies from package list for each repo
table_packages = []
if args.table:
    for repo in packages:
        table_packages.extend(packages[repo])
    table_packages = list(set(table_packages))
else:
    for repo in repo_list:
        packages[repo] = list(set(packages[repo]))

# Some verbose to tell the user, how many packages were given to the script.
if args.verbose:
    for repo in packages:
        print(trm.sep())
        print("Repository: "+repo)
        print("Total: "+str(len(packages[repo])))
        print(trm.sep())

# For every repo specified, check the availability of packages given.
verdict_dict = {}
for repo in repo_list:
    verdict_dict[repo] = {}
    verdict_dict[repo]['ok'] = []
    verdict_dict[repo]['miss'] = []
    repo_path = os.path.join(package_cache, repo)
    if args.table:
        package_list = table_packages
    else:
        package_list = packages[repo]
    if os.path.isdir(repo_path):
        for package in package_list:
            if package.startswith('lib'):
                filename = package[0:4]
            else:
                filename = package[0]
            if check(repo_path, filename, package):
                verdict_dict[repo]['ok'].append(package)
            else:
                verdict_dict[repo]['miss'].append(package)
        verdict_dict[repo]['ok'].sort()
        verdict_dict[repo]['miss'].sort()
    else:
        sys.exit(repo_path + " is not a directory!")

# Output either as a table or as a list
color = None
if args.table:
    header = ['Package']
    header.extend(repo_list)
    x = PrettyTable(header)
    table_packages.sort()
    for package in table_packages:
        row_values = [package]
        green = False
        red = False
        for repo in repo_list: 
            if package in verdict_dict[repo]['ok']:
                row_values.append('X')
                green = True
            else:
                row_values.append('')
                red = True
        if args.color:
            if green and red:
                row_values[0] = Fore.YELLOW + package + Style.RESET_ALL
            elif not green and red:
                row_values[0] = Fore.RED + package + Style.RESET_ALL
            elif green and not red:
                row_values[0] = Fore.GREEN + package + Style.RESET_ALL
        if (green and red):
            x.add_row(row_values)
        if args.ok and (green and not red):
            x.add_row(row_values)
        if args.missing and (red and not green):
            x.add_row(row_values)
    print(x)
else:
    for repo in repo_list:
        prefix = ""
        color = None
        if len(verdict_dict) > 1:
            print(repo)
        if args.ok:
            if args.indent:
                prefix = "  "
            if args.color:
                color = Fore.GREEN
            if args.missing:
                print(prefix+"AVAILABLE:")
                prefix = prefix * 2
            for package in verdict_dict[repo]['ok']:
                color_print(prefix+package, color)
        if args.missing:
            if args.indent:
                prefix = "  "
            if args.color:
                color = Fore.RED
            if args.ok:
                print(prefix+"MISSING:")
                prefix = prefix * 2
            for package in verdict_dict[repo]["miss"]:
                color_print(prefix+package, color)
