python-gammu
============

.. image:: https://travis-ci.org/gammu/python-gammu.svg?branch=master
    :target: https://travis-ci.org/gammu/python-gammu

.. image:: https://www.codacy.com/project/badge/c7e87df480fb4609aa48482873f5c46b
    :target: https://www.codacy.com/public/nijel/python-gammu

.. image:: https://scrutinizer-ci.com/g/gammu/python-gammu/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/gammu/python-gammu/?branch=master

.. image:: https://landscape.io/github/gammu/python-gammu/master/landscape.svg?style=flat
   :target: https://landscape.io/github/gammu/python-gammu/master

.. image:: https://coveralls.io/repos/gammu/python-gammu/badge.svg
    :target: https://coveralls.io/r/gammu/python-gammu

.. image:: https://buildtimetrend.herokuapp.com/badge/gammu/python-gammu/latest
    :target: https://buildtimetrend.herokuapp.com/dashboard/gammu/python-gammu

.. image:: https://scan.coverity.com/projects/4837/badge.svg
    :target: https://scan.coverity.com/projects/4837

.. image:: https://img.shields.io/gratipay/Gammu.svg
    :alt: Gratipay
    :target: https://gratipay.com/Gammu/

.. image:: https://www.bountysource.com/badge/team?team_id=23177&style=bounties_received
    :alt: Bountysource
    :target: https://www.bountysource.com/teams/gammu/issues?utm_source=Gammu&utm_medium=shield&utm_campaign=bounties_received

.. image:: https://img.shields.io/pypi/dm/python-gammu.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/python-gammu/

.. image:: https://todofy.org/b/gammu/python-gammu
    :target: https://todofy.org/r/gammu/python-gammu

Python bindings for Gammu library.

Homepage
========

<http://wammu.eu/python-gammu/>

License
=======

Copyright (C) 2003 - 2016 Michal Čihař

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

You can install in a usual way for Python modules using distutils, so use
``setup.py`` which is placed in the top level directory::

    ./setup.py build
    sudo ./setup.py install

You can also install it using pip installer::

    pip install python-gammu

Requirements
============

To compile python-gammu, you need Gammu development files (usually shipped as
``libgammu-dev`` or ``gammu-devel`` in Linux distributions) and pkg-config,
which is used to discover location of dependencies.

Documentation
=============

Please see included python documentation::

    >>> import gammu
    >>> help(gammu)

Alternatively you can use Sphinx to generate browsable version, which is
also available on-line at <http://wammu.eu/docs/manual/>.

Feedback and bug reports
========================

Any feedback is welcome, see <http://wammu.eu/support/> for information
how to contact developers.
