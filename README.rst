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

<https://wammu.eu/python-gammu/>

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

Requirements
============

To compile python-gammu, you need Gammu development files (usually shipped as
``libgammu-dev`` or ``gammu-devel`` in Linux distributions).

The location of the libraries is discovered using ``pkg-config``,
``GAMMU_PATH`` environment variable and falls back to generic locations. In
case it does not work, either install ``pkg-config`` or set ``GAMMU_PATH``.

On Linux something like this should work::

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
also available online at <https://wammu.eu/docs/manual/>.

Feedback and bug reports
========================

Any feedback is welcome, see <https://wammu.eu/support/> for information
how to contact developers.
