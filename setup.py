#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2017 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <https://wammu.eu/python-gammu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
'''
python-gammu - Phone communication libary
'''

import distutils.spawn
from setuptools import setup, Extension
import os
import platform
import codecs

# some defines
VERSION = '2.9'
GAMMU_REQUIRED = '1.37.90'
README_FILE = os.path.join(os.path.dirname(__file__), 'README.rst')
with codecs.open(README_FILE, 'r', 'utf-8') as readme:
    README = readme.read()


def check_minimum_gammu_version():
    if 'GAMMU_PATH' in os.environ:
        return
    distutils.spawn.spawn([
        'pkg-config',
        "--print-errors",
        "--atleast-version={0}".format(GAMMU_REQUIRED),
        "gammu"
    ])


def get_pkgconfig_data(args, mod, required=True):
    """Run pkg-config to and return content associated with it"""
    f = os.popen("pkg-config {0} {1}".format(" ".join(args), mod))

    line = f.readline()
    if line is not None:
        line = line.strip()

    if line is None or line == "":
        if required:
            raise Exception(
                "Cannot determine '{0}' from pkg-config".format(" ".join(args))
            )
        else:
            return ""

    return line


def get_module():
    path = os.environ.get('GAMMU_PATH')
    if path:
        libs = ['Gammu', 'gsmsd']
        cflags = '-I{0}'.format(
            os.path.join(path, 'include', 'gammu')
        )
        if platform.system() == 'Windows':
            libs.append('Advapi32')
            ldflags = '/LIBPATH:{0}'.format(
                os.path.join(path, 'lib')
            )
        else:
            ldflags = '-L{0}'.format(
                os.path.join(path, 'lib')
            )
    else:
        libs = get_pkgconfig_data(["--libs-only-l"], "gammu gammu-smsd", False)
        libs = libs.replace('-l', '').split()
        ldflags = get_pkgconfig_data(["--libs-only-L"], "gammu gammu-smsd", False)
        cflags = get_pkgconfig_data(["--cflags"], "gammu gammu-smsd", False)
    module = Extension(
        'gammu._gammu',
        libraries=libs,
        include_dirs=['include/'],
        sources=[
            'gammu/src/errors.c',
            'gammu/src/data.c',
            'gammu/src/misc.c',
            'gammu/src/convertors/misc.c',
            'gammu/src/convertors/string.c',
            'gammu/src/convertors/time.c',
            'gammu/src/convertors/base.c',
            'gammu/src/convertors/sms.c',
            'gammu/src/convertors/memory.c',
            'gammu/src/convertors/todo.c',
            'gammu/src/convertors/calendar.c',
            'gammu/src/convertors/bitmap.c',
            'gammu/src/convertors/ringtone.c',
            'gammu/src/convertors/backup.c',
            'gammu/src/convertors/file.c',
            'gammu/src/convertors/call.c',
            'gammu/src/convertors/wap.c',
            'gammu/src/convertors/diverts.c',
            'gammu/src/gammu.c',
            'gammu/src/smsd.c',
        ]
    )
    module.extra_compile_args.append(
        '-DPYTHON_GAMMU_VERSION="{0}"'.format(VERSION)
    )
    if cflags:
        module.extra_compile_args.append(cflags)
    if ldflags:
        module.extra_link_args.append(ldflags)
    return module


check_minimum_gammu_version()
setup(
    name='python-gammu',
    version=VERSION,
    description='Gammu bindings',
    long_description=README,
    author='Michal Čihař',
    author_email='michal@cihar.com',
    platforms=['Linux', 'Mac OSX', 'Windows XP/2000/NT', 'Windows 95/98/ME'],
    keywords=[
        'mobile', 'phone', 'SMS', 'contact', 'gammu', 'calendar', 'todo'
    ],
    license='GPLv2+',
    url='https://wammu.eu/python-gammu/',
    download_url='https://wammu.eu/download/python-gammu/',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: '
        'GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Telephony',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware',
    ],
    test_suite="test",
    packages=['gammu'],
    ext_modules=[get_module()]
)
