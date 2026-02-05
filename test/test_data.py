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
import unittest

import gammu
import gammu.data


class DataTest(unittest.TestCase):
    def test_connections(self):
        assert "at" in gammu.data.Connections

    def test_errors(self):
        assert "ERR_INSTALL_NOT_FOUND" in gammu.data.Errors
        assert gammu.data.ErrorNumbers[73] == "ERR_NETWORK_ERROR"

    def test_gsm_networks(self):
        """Test that GSMNetworks dictionary is available and contains expected data."""
        # GSMNetworks should be a dictionary available from gammu module
        assert isinstance(gammu.GSMNetworks, dict)
        # Should have at least some networks
        assert len(gammu.GSMNetworks) > 0
        # Test a known network code (Finland Elisa)
        # Network code "244 05" should map to "Elisa"
        if "244 05" in gammu.GSMNetworks:
            assert gammu.GSMNetworks["244 05"] == "Elisa"

    def test_gsm_countries(self):
        """Test that GSMCountries dictionary is available and contains expected data."""
        # GSMCountries should be a dictionary available from gammu module
        assert isinstance(gammu.GSMCountries, dict)
        # Should have at least some countries
        assert len(gammu.GSMCountries) > 0
        # Test a known country code (Finland)
        if "244" in gammu.GSMCountries:
            assert gammu.GSMCountries["244"] == "Finland"
