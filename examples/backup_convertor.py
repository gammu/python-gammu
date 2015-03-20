#!/usr/bin/env python

from __future__ import print_function
import gammu

import sys
if len(sys.argv) != 3:
    print(
        'This requires two parameter with file names!'
        ' First is input, second output.'
    )
    sys.exit(1)

backup = gammu.ReadBackup(sys.argv[1])
gammu.SaveBackup(sys.argv[2], backup)
