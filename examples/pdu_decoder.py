#!/usr/bin/env python

from __future__ import print_function
import gammu

import sys
if len(sys.argv) != 2:
    print('This requires parameter with hex encoded PDU data!')
    sys.exit(1)

# Global debug level
gammu.SetDebugFile(sys.stderr)
gammu.SetDebugLevel('textall')

sms = gammu.DecodePDU(sys.argv[1].decode('hex'))
print(sms)
