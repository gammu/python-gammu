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

import binascii
import unittest

import gammu


class SurrogateTest(unittest.TestCase):
    """Test handling of Unicode surrogates in PDU decoding."""

    def test_invalid_high_surrogate_alone(self):
        """Test that a high surrogate without a low surrogate is replaced with U+FFFD."""
        # Create a PDU with an invalid high surrogate (0xD800) followed by a regular char
        # PDU structure: SMSC info + PDU type + sender + ... + UDH + text
        # We'll create a simple SMS with UCS2 encoding containing:
        # High surrogate 0xD800 followed by 'A' (0x0041)

        # This is a crafted PDU with invalid surrogate sequence in the text
        # Format: deliver SMS, UCS2 encoding, with text containing D800 (high surrogate) + 0041 ('A')
        pdu_hex = (
            "07911234567890F0"  # SMSC
            "04"  # PDU type: SMS-DELIVER
            "0B"  # Sender address length
            "911234567890F0"  # Sender number
            "00"  # Protocol identifier
            "08"  # Data coding scheme (UCS2)
            "11111111111111"  # Timestamp
            "04"  # User data length (4 bytes = 2 UCS2 chars)
            "D80000410000"  # Text: D800 (invalid surrogate) + 0041 ('A') + 0000 (null terminator)
        )

        pdu_data = binascii.unhexlify(pdu_hex.encode("ascii"))

        # This should not raise UnicodeEncodeError
        try:
            sms = gammu.DecodePDU(pdu_data)
            text = sms.get("Text", "")

            # Should be able to encode to UTF-8 without error
            text.encode("utf-8")

            # The invalid surrogate should be replaced with replacement character
            # U+FFFD (REPLACEMENT CHARACTER)
            self.assertIn("\ufffd", text)

        except UnicodeEncodeError as e:
            self.fail(f"UnicodeEncodeError should not be raised: {e}")

    def test_valid_surrogate_pair(self):
        """Test that valid surrogate pairs are correctly decoded to supplementary characters."""
        # Valid surrogate pair: D800 DC00 = U+10000
        # Create a PDU with a valid surrogate pair
        pdu_hex = (
            "07911234567890F0"  # SMSC
            "04"  # PDU type: SMS-DELIVER
            "0B"  # Sender address length
            "911234567890F0"  # Sender number
            "00"  # Protocol identifier
            "08"  # Data coding scheme (UCS2)
            "11111111111111"  # Timestamp
            "04"  # User data length (4 bytes = 2 UCS2 chars forming 1 surrogate pair)
            "D800DC000000"  # Text: D800 DC00 (valid surrogate pair) + 0000 (null terminator)
        )

        pdu_data = binascii.unhexlify(pdu_hex.encode("ascii"))

        try:
            sms = gammu.DecodePDU(pdu_data)
            text = sms.get("Text", "")

            # Should be able to encode to UTF-8 without error
            encoded = text.encode("utf-8")

            # Valid surrogate pair D800 DC00 should decode to U+10000
            # U+10000 in UTF-8 is F0 90 80 80
            self.assertIn(b"\xf0\x90\x80\x80", encoded)

        except UnicodeEncodeError as e:
            self.fail(f"UnicodeEncodeError should not be raised: {e}")

    def test_high_surrogate_with_invalid_low(self):
        """Test that a high surrogate followed by invalid low surrogate is handled."""
        # High surrogate 0xD800 followed by invalid value 0x0100 (not a low surrogate)
        pdu_hex = (
            "07911234567890F0"  # SMSC
            "04"  # PDU type: SMS-DELIVER
            "0B"  # Sender address length
            "911234567890F0"  # Sender number
            "00"  # Protocol identifier
            "08"  # Data coding scheme (UCS2)
            "11111111111111"  # Timestamp
            "04"  # User data length
            "D80001000000"  # Text: D800 (high surrogate) + 0100 (invalid - not low surrogate)
        )

        pdu_data = binascii.unhexlify(pdu_hex.encode("ascii"))

        try:
            sms = gammu.DecodePDU(pdu_data)
            text = sms.get("Text", "")

            # Should be able to encode to UTF-8 without error
            text.encode("utf-8")

            # The invalid surrogate should be replaced
            self.assertIn("\ufffd", text)

        except UnicodeEncodeError as e:
            self.fail(f"UnicodeEncodeError should not be raised: {e}")

    def test_low_surrogate_alone(self):
        """Test that a standalone low surrogate is replaced with U+FFFD."""
        # Low surrogate 0xDC00 alone (without preceding high surrogate)
        pdu_hex = (
            "07911234567890F0"  # SMSC
            "04"  # PDU type: SMS-DELIVER
            "0B"  # Sender address length
            "911234567890F0"  # Sender number
            "00"  # Protocol identifier
            "08"  # Data coding scheme (UCS2)
            "11111111111111"  # Timestamp
            "04"  # User data length
            "DC0000410000"  # Text: DC00 (standalone low surrogate) + 0041 ('A')
        )

        pdu_data = binascii.unhexlify(pdu_hex.encode("ascii"))

        try:
            sms = gammu.DecodePDU(pdu_data)
            text = sms.get("Text", "")

            # Should be able to encode to UTF-8 without error
            text.encode("utf-8")

            # The standalone low surrogate should be replaced
            self.assertIn("\ufffd", text)

        except UnicodeEncodeError as e:
            self.fail(f"UnicodeEncodeError should not be raised: {e}")


if __name__ == "__main__":
    unittest.main()
