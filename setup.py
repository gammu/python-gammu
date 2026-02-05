#!/usr/bin/env python
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
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
"""python-gammu - Phone communication library."""

import glob
import os
import platform
import subprocess  # noqa: S404
import sys

from packaging.version import parse
from setuptools import Extension, setup

# some defines
VERSION = "3.2.4"
GAMMU_REQUIRED = "1.37.90"


class GammuConfig:
    def __init__(self) -> None:
        self.on_windows = platform.system() == "Windows"
        self.has_pkgconfig = self.check_pkconfig()
        self.has_env = "GAMMU_PATH" in os.environ
        self.path = self.lookup_path()
        self.use_pkgconfig = self.has_pkgconfig and not self.has_env

    def check_pkconfig(self) -> bool | None:
        try:
            subprocess.check_output(["pkg-config", "--help"])
            return True
        except (subprocess.CalledProcessError, OSError):
            return False

    def config_path(self, base):
        return os.path.join(base, "include", "gammu", "gammu-config.h")

    def lookup_path(self):
        if self.has_env:
            paths = [os.environ["GAMMU_PATH"]]
        elif self.on_windows:
            paths = [
                "C:\\Gammu",
                "C:\\Program Files\\Gammu",
                "C:\\Program Files (x86)\\Gammu",
            ]
            paths += glob.glob("C:\\Program Files\\Gammu*")
            paths += glob.glob("C:\\Program Files (x86)\\Gammu*")
        else:
            paths = ["/usr/local/", "/usr/"]
            paths += glob.glob("/opt/gammu*")

        for path in paths:
            include = self.config_path(path)
            if os.path.exists(include):
                return path
        return None

    def check_version(self) -> None:
        if self.use_pkgconfig:
            try:
                subprocess.check_output(  # noqa: S603
                    [
                        "pkg-config",
                        "--print-errors",
                        f"--atleast-version={GAMMU_REQUIRED}",
                        "gammu",
                        "gammu-smsd",
                    ]
                )
                return
            except subprocess.CalledProcessError:
                print("Can not find supported Gammu version using pkg-config!")
                sys.exit(100)

        if self.path is None:
            print("Failed to find Gammu!")
            print("Either it is not installed or not found.")
            print("After install Gammu ensure that setup finds it by any of:")
            print(" * Specify path to it using GAMMU_PATH in environment.")
            print(" * Install pkg-config.")
            sys.exit(101)

        version = None
        with open(self.config_path(self.path)) as handle:
            for line in handle:
                if line.startswith("#define GAMMU_VERSION "):
                    version = parse(line.split('"')[1])

        if version is None or version < parse(GAMMU_REQUIRED):
            print("Too old Gammu version, please upgrade!")
            sys.exit(100)

    def get_libs(self):
        if self.use_pkgconfig:
            output = subprocess.check_output(
                ["pkg-config", "--libs-only-l", "gammu", "gammu-smsd"]
            ).decode("utf-8")
            return output.replace("-l", "").strip().split()
        libs = ["Gammu", "gsmsd"]
        if self.on_windows:
            libs.extend(("Advapi32", "shfolder", "shell32"))
        else:
            libs.append("m")
        return libs

    def get_cflags(self):
        if self.use_pkgconfig:
            return (
                subprocess.check_output(
                    ["pkg-config", "--cflags", "gammu", "gammu-smsd"]
                )
                .decode("utf-8")
                .strip()
            )
        return "-I{}".format(os.path.join(self.path, "include", "gammu"))

    def get_ldflags(self):
        if self.use_pkgconfig:
            return (
                subprocess.check_output(
                    ["pkg-config", "--libs-only-L", "gammu", "gammu-smsd"]
                )
                .decode("utf-8")
                .strip()
            )
        if self.on_windows:
            return "/LIBPATH:{}".format(os.path.join(self.path, "lib"))
        return "-L{}".format(os.path.join(self.path, "lib"))


def get_module():
    config = GammuConfig()
    config.check_version()

    module = Extension(
        "gammu._gammu",
        define_macros=[
            ("PYTHON_GAMMU_MAJOR_VERSION", VERSION.split(".", maxsplit=1)[0]),
            ("PYTHON_GAMMU_MINOR_VERSION", VERSION.split(".")[1]),
        ],
        libraries=config.get_libs(),
        include_dirs=["include/"],
        sources=[
            "gammu/src/errors.c",
            "gammu/src/data.c",
            "gammu/src/misc.c",
            "gammu/src/convertors/misc.c",
            "gammu/src/convertors/string.c",
            "gammu/src/convertors/time.c",
            "gammu/src/convertors/base.c",
            "gammu/src/convertors/sms.c",
            "gammu/src/convertors/memory.c",
            "gammu/src/convertors/todo.c",
            "gammu/src/convertors/calendar.c",
            "gammu/src/convertors/bitmap.c",
            "gammu/src/convertors/ringtone.c",
            "gammu/src/convertors/backup.c",
            "gammu/src/convertors/file.c",
            "gammu/src/convertors/call.c",
            "gammu/src/convertors/wap.c",
            "gammu/src/convertors/diverts.c",
            "gammu/src/gammu.c",
            "gammu/src/smsd.c",
        ],
    )
    flags = config.get_cflags()
    if flags:
        module.extra_compile_args.append(flags)
    flags = config.get_ldflags()
    if flags:
        module.extra_link_args.append(flags)
    return module


setup(
    ext_modules=[get_module()],
)
