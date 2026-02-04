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
"""
Example demonstrating how to get network information and look up network names.

When GetNetworkInfo() returns an empty NetworkName, you can use the
gammu.GSMNetworks dictionary to look up the network name by its NetworkCode.
The NetworkCode is returned by the phone even when NetworkName is empty.

This is useful because many phones don't return the network name, but the
network code can be looked up in Gammu's network database.
"""

import sys

import gammu


def get_network_info_with_name(state_machine):
    """
    Get network information and look up network name if it's empty.

    The phone returns NetworkCode (e.g., "240 24") even when NetworkName
    is empty. We can use gammu.GSMNetworks to look up the network name.
    """
    # Get network info from phone
    netinfo = state_machine.GetNetworkInfo()

    print("Network Information:")
    print("=" * 50)
    print(f"Network Code: {netinfo['NetworkCode']}")
    print(f"Network Name (from phone): {netinfo['NetworkName']}")

    # If NetworkName is empty, look it up in the GSMNetworks database
    if not netinfo["NetworkName"] and netinfo["NetworkCode"]:
        network_code = netinfo["NetworkCode"]
        if network_code in gammu.GSMNetworks:
            network_name = gammu.GSMNetworks[network_code]
            print(f"Network Name (from DB): {network_name}")
        else:
            print(f"Network Name (from DB): Unknown network code '{network_code}'")

    print(f"State: {netinfo['State']}")
    print(f"LAC: {netinfo['LAC']}")
    print(f"CID: {netinfo['CID']}")

    if "GPRS" in netinfo:
        print(f"GPRS: {netinfo['GPRS']}")

    return netinfo


def main():
    """Main function to demonstrate network info lookup."""
    # Create state machine
    state_machine = gammu.StateMachine()

    # Read configuration from default location (~/.gammurc or /etc/gammurc)
    # You can also specify a config file: state_machine.ReadConfig(Filename="gammurc")
    state_machine.ReadConfig()

    # Connect to phone
    state_machine.Init()

    # Get and display network information with name lookup
    get_network_info_with_name(state_machine)

    # You can also explore available networks in the database
    print("\n" + "=" * 50)
    print("Example: Browsing the GSMNetworks database")
    print("=" * 50)
    print(f"Total networks in database: {len(gammu.GSMNetworks)}")

    # Show a few example networks
    print("\nSome example networks:")
    example_codes = ["240 24", "244 05", "310 260", "234 10"]
    for code in example_codes:
        if code in gammu.GSMNetworks:
            print(f"  {code}: {gammu.GSMNetworks[code]}")


if __name__ == "__main__":
    try:
        main()
    except gammu.GSMError as e:
        print(f"Error: {e}")
        sys.exit(1)
