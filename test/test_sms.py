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
import datetime
import os
import sys
import unittest

import pytest

import gammu

PDU_DATA = binascii.unhexlify(
    b"079124602009999002AB098106845688F8907080517375809070805183018000"
)

MESSAGE = (
    ".........1.........2.........3.........4.........5.........6.........7"
    ".........8.........9........0.........1.........2.........3.........4"
    ".........5.........6.........7.........8.........9........0.........1"
    ".........2.........3.........4.........5.........6.........7.........8"
    ".........9........0"
)
UNICODE = (
    ".........1ě........2..ř......3...žš....4....ý....5....á....6....á....7"
    ".........8.........9........0.........1.........2.........3.........4"
    ".........5.........6.........7.........8.........9........0.........1"
    ".........2.........3.........4.........5.........6.........7.........8"
    ".........9....č...0"
)
GSM = (
    ".........1$........2..Ø......3...åÅ....4....Λ....5....Æ....6....ñ....7"
    ".........8.........9........0.........1.........2.........3.........4"
    ".........5.........6.........7.........8.........9........0.........1"
    ".........2.........3.........4.........5.........6.........7.........8"
    ".........9....¥€..0"
)


class PDUTest(unittest.TestCase):
    def setUp(self) -> None:
        if "GAMMU_DEBUG" in os.environ:
            gammu.SetDebugFile(sys.stderr)
            gammu.SetDebugLevel("textall")

    def test_decode(self) -> None:
        sms = gammu.DecodePDU(PDU_DATA)
        assert sms["Number"] == "604865888"
        assert sms["Text"] == "Delivered"

    def test_decode_rejects_truncated_frame(self) -> None:
        with pytest.raises(gammu.ERR_CORRUPTED):
            gammu.DecodePDU(b"")

    def test_special_decoders_reject_malformed_data(self) -> None:
        for value in (
            "004000810004000000000000000807120500ffff0000",
            "00400081000400000000000000100b0504158a00000003ce010130017f7f",
        ):
            decoded = gammu.DecodePDU(bytes.fromhex(value))
            assert gammu.DecodeSMS([decoded]) is None

    def test_encode_pdu_rejects_extension_overflow(self) -> None:
        sms = gammu.EncodeSMS(
            {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": "^" * 80}]}
        )[0]
        sms["Text"] = "^" * 160
        with pytest.raises(gammu.ERR_INVALIDDATA):
            gammu.EncodePDU(sms)

    def test_encode_rejects_unrepresentable_multipart(self) -> None:
        with pytest.raises(gammu.ERR_INVALIDDATA):
            gammu.EncodeSMS(
                {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": "A" * 40000}]}
            )

    def test_conversion_limits_reject_instead_of_truncate(self) -> None:
        sms = gammu.DecodePDU(
            bytes.fromhex(
                "0791361907001003B17A0C913619397750320000AD11CD701E340FB3C3F23CC81D0689C3BF"
            )
        )

        oversized_binary = dict(sms, Coding="8bit", Text=b"A" * 651)
        with pytest.raises(ValueError, match="SMS text is too large"):
            gammu.EncodePDU(oversized_binary)

        oversized_udh = dict(sms)
        oversized_udh["UDH"] = {"Type": "UserUDH", "Text": b"\x00" * 141}
        with pytest.raises(ValueError, match="UDH is too large"):
            gammu.EncodePDU(oversized_udh)

        with pytest.raises(ValueError, match="MultiSMS has too many entries"):
            gammu.DecodeSMS([sms] * 51)

        with pytest.raises(ValueError, match="Too many SMS info entries"):
            gammu.EncodeSMS({"Entries": [{}] * 50})

    def do_smstest(self, smsinfo, expected) -> None:
        # encode SMSes
        sms = gammu.EncodeSMS(smsinfo)

        # decode back SMSes
        decodedsms = gammu.DecodeSMS(sms)

        # compare text
        assert decodedsms["Entries"][0]["Buffer"] == expected

        # do conversion to PDU
        pdu = [gammu.EncodePDU(s) for s in sms]

        # Convert back
        pdusms = [gammu.DecodePDU(p) for p in pdu]

        # decode back SMS from PDU
        decodedsms = gammu.DecodeSMS(pdusms)

        # compare PDU results
        assert decodedsms["Entries"][0]["Buffer"] == expected

    def test_encode_plain(self) -> None:
        smsinfo = {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": MESSAGE}]}
        self.do_smstest(smsinfo, MESSAGE)

    def test_encode_gsm(self) -> None:
        smsinfo = {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": GSM}]}
        self.do_smstest(smsinfo, GSM)

    def test_encode_unicode(self) -> None:
        smsinfo = {
            "Entries": [{"ID": "ConcatenatedTextLong", "Buffer": UNICODE}],
            "Unicode": True,
        }
        self.do_smstest(smsinfo, UNICODE)

    def test_link(self) -> None:
        # SMS info about message
        smsinfo = {"Entries": [{"ID": "ConcatenatedTextLong", "Buffer": MESSAGE}]}

        # encode SMS
        sms = gammu.EncodeSMS(smsinfo)

        # link SMS
        linked = gammu.LinkSMS([[sms[0]], [sms[1]]], True)

        # decode back SMS
        decodedsms = gammu.DecodeSMS(linked[0])

        # compare results
        assert decodedsms["Entries"][0]["Buffer"], MESSAGE

    def test_mms_decode(self) -> None:
        message = [
            {
                "RejectDuplicates": 0,
                "SMSCDateTime": datetime.datetime(2010, 7, 22, 17, 4, 11),
                "Class": -1,
                "Name": "",
                "InboxFolder": 0,
                "Text": (
                    b"\x04\x06\x03\xbe\xaf\x84\x8c\x82\x981277970059\x00\x8d\x92"
                    b"\x89\x19\x80\x16\x0433707520030/TYPE=PLMN\x00\x96yBO\x00"
                    b'\x8a\x80\x8e\x01"\x88\x04\x81\x02\x0b\xb8\x83'
                    b"http://mmsc.labmctel.fr:9090/m33\x00"
                ),
                "SMSC": {
                    "DefaultNumber": "",
                    "Format": "Text",
                    "Number": "+33700065030",
                    "Validity": "NA",
                    "Location": 0,
                    "Name": "",
                },
                "ReplaceMessage": 0,
                "Coding": "8bit",
                "Number": "33707520030",
                "DateTime": datetime.datetime(2010, 7, 1, 9, 40, 21),
                "DeliveryStatus": 0,
                "State": "UnSent",
                "MessageReference": 0,
                "Length": 99,
                "Location": 0,
                "Memory": "",
                "ReplyViaSameSMSC": 0,
                "UDH": {
                    "Text": b"\x06\x05\x04\x0b\x84#\xf0",
                    "ID16bit": -1,
                    "AllParts": -1,
                    "ID8bit": -1,
                    "PartNumber": -1,
                    "Type": "UserUDH",
                },
                "Type": "Deliver",
                "Folder": 2,
            }
        ]

        decoded = gammu.DecodeSMS(message)
        assert (
            decoded["Entries"][0]["MMSIndicator"]["Address"]
            == "http://mmsc.labmctel.fr:9090/m33"
        )

    def test_counter(self) -> None:
        assert gammu.SMSCounter("foobar") == (1, 154)

    def test_counter_long(self) -> None:
        assert gammu.SMSCounter(
            "foobar fjsa;kjfkasdjfkljsklfjaskdljfkljasdfkljqilui143uu51o23rjhskdf jasdklfjasdklf jasdfkljasdlkfj;asd;lfjaskdljf431ou983jdfaskljfklsdjdkljasfl sdfjasdfkl jafklsda"
        ) == (2, 156)
