python-gammu
============

Python bindings for the `Gammu library <https://wammu.eu/gammu/>`_.

.. image:: https://github.com/gammu/python-gammu/actions/workflows/test.yml/badge.svg
    :target: https://github.com/gammu/python-gammu/actions/workflows/test.yml

.. image:: https://img.shields.io/liberapay/receives/Gammu.svg
    :alt: Liberapay
    :target: https://liberapay.com/Gammu/donate

.. image:: https://img.shields.io/pypi/v/python-gammu.svg
    :alt: PyPI
    :target: https://pypi.org/project/python-gammu/

Homepage
========

<https://github.com/gammu/python-gammu/>

License
=======

Copyright (C) Michal Čihař <michal@cihar.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Installing
==========

Install it using pip installer::

    pip install python-gammu

Linux wheels
============

Binary wheels are available for CPython 3.10 and newer on 64-bit x86 and ARM
Linux systems using glibc 2.28 or newer. They include a minimal, statically
linked Gammu library, so installing Gammu separately is not necessary.

The wheels support core phone protocols, serial connections, converters,
backups, and the SMSD file and null services. Bluetooth, native USB, IrDA,
database-backed SMSD services, CURL, GLib/GObject, systemd, gettext, and iconv
integration are not included.

.. renovate: datasource=github-release-attachments depName=gammu/gammu versioning=loose

The bundled Gammu 1.43.3 library is licensed under GPL-2.0-or-later. The
corresponding source archive is available from:

https://github.com/gammu/gammu/releases/download/1.43.3/Gammu-1.43.3.tar.gz

To use those optional features, install a fully featured Gammu development
package and force a source build::

    pip install --no-binary python-gammu python-gammu

Requirements
============

To compile python-gammu from source, you need Gammu development files (usually
shipped as ``libgammu-dev`` or ``gammu-devel`` in Linux distributions).

The location of the libraries is discovered using ``pkg-config``,
``GAMMU_PATH`` environment variable and falls back to generic locations. In
case it does not work, either install ``pkg-config`` or set ``GAMMU_PATH``.

Any feedback is welcome, see the `project homepage <https://github.com/gammu/python-gammu/>`_
for information how to contact developers.
    GAMMU_PATH=/opt/gammu pip install .

On Windows::

    SET GAMMU_PATH="C:\Gammu"
    pip install .


Documentation
=============

Please see included python documentation::

    >>> import gammu
    >>> help(gammu)

Alternatively you can use Sphinx to generate browsable version, which is
also available online at <https://docs.gammu.org/>.

Feedback and bug reports
========================

Any feedback is welcome, see <https://github.com/gammu/python-gammu/> for information
how to contact developers.
