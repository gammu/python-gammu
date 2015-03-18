# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This file is part of Gammu <http://wammu.eu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import unicode_literals
import unittest
import doctest
import gammu
import sys


PDU_DATA = '079124602009999002AB098106845688F8907080517375809070805183018000'
MESSAGE = (
    '.........1.........2.........3.........4.........5.........6.........7'
    '.........8.........9........0.........1.........2.........3.........4'
    '.........5.........6.........7.........8.........9........0.........1'
    '.........2.........3.........4.........5.........6.........7.........8'
    '.........9........0'
)
UNICODE = (
    '.........1ě........2..ř......3...žš....4....ý....5....á....6....á....7'
    '.........8.........9........0.........1.........2.........3.........4'
    '.........5.........6.........7.........8.........9........0.........1'
    '.........2.........3.........4.........5.........6.........7.........8'
    '.........9....č...0'
)
GSM = (
    '.........1$........2..Ø......3...åÅ....4....Λ....5....Æ....6....ñ....7'
    '.........8.........9........0.........1.........2.........3.........4'
    '.........5.........6.........7.........8.........9........0.........1'
    '.........2.........3.........4.........5.........6.........7.........8'
    '.........9....¥€..0'
)


class PDUTest(unittest.TestCase):
    def setUp(self):
        gammu.SetDebugFile(sys.stderr)
        gammu.SetDebugLevel('textall')

    def test_decode(self):
        sms = gammu.DecodePDU(PDU_DATA.decode('hex'))
        self.assertEqual(sms['Number'], '604865888')
        self.assertEqual(sms['Text'], 'Delivered')

    def do_smstest(self, smsinfo, expected):
        # encode SMSes
        sms = gammu.EncodeSMS(smsinfo)

        # decode back SMSes
        decodedsms = gammu.DecodeSMS(sms)

        # compare text
        self.assertEqual(decodedsms['Entries'][0]['Buffer'], expected)

        # do conversion to PDU
        pdu = [gammu.EncodePDU(s) for s in sms]

        # Convert back
        pdusms = [gammu.DecodePDU(p) for p in pdu]

        # decode back SMS from PDU
        decodedsms = gammu.DecodeSMS(pdusms)

        # compare PDU results
        self.assertEqual(decodedsms['Entries'][0]['Buffer'], expected)

    def test_encode_plain(self):
        smsinfo = {
            'Entries': [{'ID': 'ConcatenatedTextLong', 'Buffer': MESSAGE}]
        }
        self.do_smstest(smsinfo, MESSAGE)

    def test_encode_gsm(self):
        smsinfo = {
            'Entries': [{'ID': 'ConcatenatedTextLong', 'Buffer': GSM}]
        }
        self.do_smstest(smsinfo, GSM)

    def test_encode_unicode(self):
        smsinfo = {
            'Entries': [{'ID': 'ConcatenatedTextLong', 'Buffer': UNICODE}],
            'Unicode': True
        }
        self.do_smstest(smsinfo, UNICODE)
