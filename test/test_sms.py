# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2016 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <http://wammu.eu/python-gammu/>
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
from __future__ import unicode_literals
import datetime
import unittest
import gammu
import sys
import os
import binascii

PDU_DATA = binascii.unhexlify(
    b'079124602009999002AB098106845688F8907080517375809070805183018000'
)

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
        if 'GAMMU_DEBUG' in os.environ:
            gammu.SetDebugFile(sys.stderr)
            gammu.SetDebugLevel('textall')

    def test_decode(self):
        sms = gammu.DecodePDU(PDU_DATA)
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

    def test_link(self):
        # SMS info about message
        smsinfo = {
            'Entries': [{'ID': 'ConcatenatedTextLong', 'Buffer': MESSAGE}]
        }

        # encode SMS
        sms = gammu.EncodeSMS(smsinfo)

        # link SMS
        linked = gammu.LinkSMS([[sms[0]], [sms[1]]], True)

        # decode back SMS
        decodedsms = gammu.DecodeSMS(linked[0])

        # compare results
        self.assertTrue(decodedsms['Entries'][0]['Buffer'], MESSAGE)

    def test_mms_decode(self):
        message = [{
            'RejectDuplicates': 0,
            'SMSCDateTime': datetime.datetime(2010, 7, 22, 17, 4, 11),
            'Class': -1,
            'Name': '',
            'InboxFolder': 0,
            'Text': (
                b'\x04\x06\x03\xbe\xaf\x84\x8c\x82\x981277970059\x00\x8d\x92'
                b'\x89\x19\x80\x16\x0433707520030/TYPE=PLMN\x00\x96yBO\x00'
                b'\x8a\x80\x8e\x01"\x88\x04\x81\x02\x0b\xb8\x83'
                b'http://mmsc.labmctel.fr:9090/m33\x00'
            ),
            'SMSC': {
                'DefaultNumber': '',
                'Format': 'Text',
                'Number': '+33700065030',
                'Validity': 'NA',
                'Location': 0,
                'Name': ''
            },
            'ReplaceMessage': 0,
            'Coding': '8bit',
            'Number': '33707520030',
            'DateTime': datetime.datetime(2010, 7, 1, 9, 40, 21),
            'DeliveryStatus': 0,
            'State': 'UnSent',
            'MessageReference': 0,
            'Length': 99,
            'Location': 0,
            'Memory': '',
            'ReplyViaSameSMSC': 0,
            'UDH': {
                'Text': b'\x06\x05\x04\x0b\x84#\xf0',
                'ID16bit': -1,
                'AllParts': -1,
                'ID8bit': -1,
                'PartNumber': -1,
                'Type': 'UserUDH'
            },
            'Type': 'Deliver',
            'Folder': 2
        }]

        decoded = gammu.DecodeSMS(message)
        self.assertEqual(
            decoded['Entries'][0]['MMSIndicator']['Address'],
            'http://mmsc.labmctel.fr:9090/m33'
        )

    def test_counter(self):
        self.assertEqual(
            gammu.SMSCounter('foobar'),
            (1, 154)
        )

    def test_counter_long(self):
        self.assertEqual(
            gammu.SMSCounter(
                'foobar fjsa;kjfkasdjfkljsklfjaskdljfkljasdfkljqilui143uu51o2'
                '3rjhskdf jasdklfjasdklf jasdfkljasdlkfj;asd;lfjaskdljf431ou9'
                '83jdfaskljfklsdjdkljasfl sdfjasdfkl jafklsda'
            ),
            (2, 156)
        )
