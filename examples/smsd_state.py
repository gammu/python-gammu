#!/usr/bin/env python
# sample script to show how to get SMSD status

from __future__ import print_function
import gammu.smsd

smsd = gammu.smsd.SMSD('/etc/gammu-smsdrc')

print(smsd.GetStatus())
