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


class PDUTest(unittest.TestCase):
    def setUp(self):
        gammu.SetDebugFile(sys.stderr)
        gammu.SetDebugLevel('textall')

    def test_decode(self):
        sms = gammu.DecodePDU(PDU_DATA.decode('hex'))
        self.assertEqual(sms['Number'], '604865888')
        self.assertEqual(sms['Text'], 'Delivered')

    def test_smsinfo(self):
        # text of sms
        # SMS info about message
        smsinfo = {
            'Entries': [{'ID': 'ConcatenatedTextLong', 'Buffer': MESSAGE}]
        }

        # encode SMSes
        sms = gammu.EncodeSMS(smsinfo)

        # decode back SMSes
        decodedsms = gammu.DecodeSMS(sms)

        # compare text
        self.assertEqual(decodedsms['Entries'][0]['Buffer'], MESSAGE)

        # do conversion to PDU
        pdu = [gammu.EncodePDU(s) for s in sms]

        # Convert back
        pdusms = [gammu.DecodePDU(p) for p in pdu]

        # decode back SMS from PDU
        decodedsms = gammu.DecodeSMS(pdusms)

        # compare PDU results
        self.assertEqual(decodedsms['Entries'][0]['Buffer'], MESSAGE)
