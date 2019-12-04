# pkgmonitor

## Description

This tool saves a local name cache of configured deb repositories to disc to check the availability of packages in a given repository.

## Dependencies

* python3 (3.5.3+)
* python3-yaml
* python3-colorama
* python3-prettytable

## Usage

## rules.d

rules.d contains yaml files to alter the names of packages given as input to pkgmonitor.py.
These files are evaluated in order (ascending). The rules in these files are also evaluated in order and the first matching line is used.
If you want to use more elaborate regex expression containing sets, you need to contain your expression in quotation marks.

### Blacklist format

The REPOSITORY_NAME has to coincide with the name of the repository in repos.d (or cache/fetch, cache/packages).
packages contains a list of regular expressions which match the package name to blacklist.

```
- repo: REPOSITORY_NAME
  packages:
      - REGEX_TO_MATCH_PACKAGE_NAME_1
      - REGEX_TO_MATCH_PACKAGE_NAME_2
```

#### Examples

For repository buster, ignore all packages named "graylog-server" and "mysql-server".
Also blacklist all package names starting with the string "ruby".

```
- repo: buster
  packages:
      - ^graylog-server$
      - ^mysql-server$
      - ^ruby
```

### Rename format

```
- repo: REPOSITORY_NAME
  packages:
      - {REGEX_TO_MATCH_PACKAGE_NAME_1: REPLICATION_STRING_1}
      - {REGEX_TO_MATCH_PACKAGE_NAME_2: REPLICATION_STRING_2}
```

#### Examples

For repository buster, replace all package names beginning with "php5" with "php7.2" (php5-gd -> php7.2-gd).
Also replace a package named "python2" with the name "python3" and replace every package beginning with "mongodb" and optionally containing the set [-a-z] zero or more times with mongodb-org.

```
- repo: buster
  packages:
      - {^php5: php7.2}
      - {^python2$: python3}
      - {"^mongodb[-a-z]*$": mongodb-org}
```

## repos.d

repos.d contains yaml files to configure repositories to be downloaded and parsed by pkgmonitor-update.py.

### Format

name is used as the directory name in the caching directory.
repository contains the information needed to download all Packages.gz files for the repository.
dist specifies the RELEASE and the corresponding REPOSITORY.
arch specifies the ARCHITECTURE to download.
url specifies the download link. The dist and arch lists replace {dist} and {arch} accordingly for each element configured.

```
- name: REPOSITORY_NAME
  repository:
    - dist: [ RELEASE/REPOSITORY_1, RELEASE/REPOSITORY_2, RELEASE/REPOSITORY_3 ]
      arch: [ ARCHITECTURE_1, ARCHITECTURE_2 ]
      url: http://apt.example.org/debian/dists/{dist}/{arch}/Packages.gz
```

### Examples

Cache all packages from stretch/main, stretch/contrib, stretch/nonfree available in amd64 architecture.

```
- name: stretch
  repository:
    - dist: [ stretch/main, stretch/contrib, stretch/nonfree ]
      arch: [ binary-amd64 ]
      url: http://ftp.de.debian.org/debian/dists/{dist}/{arch}/Packages.gz
```

### pkgmonitor.py

Checks packages against its local cache.
The name of the repository corresponds to the name of the local cache.

#### Input

Accepts either or all of three input mechanisms:
```
-p / --packages : Command line option, specify packages seperated by space
-f / --file : Command line option, specify file to read from. Package names need to be seperated by newline in this file
| : Pipes the list of packages seperated by newline to the script
```
All of these input mechanisms can be combined.

#### Examples

Output all missing packages for configured repository buster:

```
./pkgmonitor.py -r buster -m -f FILE
./pkgmonitor.py -r buster -m -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -r buster -m

packagefetcher | ./pkgmonitor.py -r buster -m -p package1 package2 package3 -f FILE
```

Output all missing packages for configured repositories stretch and buster:

```
./pkgmonitor.py -r stretch buster -m -f FILE
./pkgmonitor.py -r stretch buster -m -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -r stretch buster -m

packagefetcher | ./pkgmonitor.py -r stretch buster -m -p package1 package2 package3 -f FILE
```

Output all missing packages for all configured repositories:

```
./pkgmonitor.py -am -f FILE
./pkgmonitor.py -am -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -am

packagefetcher | ./pkgmonitor.py -am -p package1 package2 package3 -f FILE
```

Output all available packages for all configured repositories:

```
./pkgmonitor.py -ao -f FILE
./pkgmonitor.py -ao -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -ao

packagefetcher | ./pkgmonitor.py -ao -p package1 package2 package3 -f FILE
```

Output both available and missing packages for all configured repositories:

```
./pkgmonitor.py -amo -f FILE
./pkgmonitor.py -amo -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -amo

packagefetcher | ./pkgmonitor.py -amo -p package1 package2 package3 -f FILE
```

Colorcode these outputs:

```
./pkgmonitor.py -amoc -f FILE
./pkgmonitor.py -amoc -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -amoc

packagefetcher | ./pkgmonitor.py -amoc -p package1 package2 package3 -f FILE
```

Output indented:

```
./pkgmonitor.py -amoci -f FILE
./pkgmonitor.py -amoci -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -amoci

packagefetcher | ./pkgmonitor.py -amoci -p package1 package2 package3 -f FILE
```

Output as table:

```
./pkgmonitor.py -amoct -f FILE
./pkgmonitor.py -amoct -p package1 package2 package3
packagefetcher | ./pkgmonitor.py -amoct

packagefetcher | ./pkgmonitor.py -amoct -p package1 package2 package3 -f FILE
```

### pkgmonitor-update.py

Fetches and parses repositories defined in repos.d/FILENAME.yaml

Options:
```
-f / --fetch : fetches the configured repositories
-u / --update : parses the fetched repositories, if the hash check failed
-r / --rebuild : skip hash check and rebuild cache
-v / --verbose : outputs the repositories to fetch, state of the hash checks and the packages the script is parsing and writing to file
```

#### Examples

Fetch all repositories and update the local cache. 
Depending on how many repositories are configured in repos.d,
adding the verbose (-v) Option might be a good idea to see what the script
is doing. Otherwise the output will be blank.

```
./pkgmonitor-update.py -fu
```

Rebuild the local cache.

```
./pkgmonitor-update.py -fr
```