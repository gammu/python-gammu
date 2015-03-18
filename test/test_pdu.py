import unittest
import doctest
import gammu
import sys

PDU_DATA = '079124602009999002AB098106845688F8907080517375809070805183018000'


class PDUTest(unittest.TestCase):
    def setUp(self):
        gammu.SetDebugFile(sys.stderr)
        gammu.SetDebugLevel('textall')

    def test_decode(self):
        sms = gammu.DecodePDU(PDU_DATA.decode('hex'))
        self.assertEqual(sms['Number'], '604865888')
        self.assertEqual(sms['Text'], 'Delivered')
