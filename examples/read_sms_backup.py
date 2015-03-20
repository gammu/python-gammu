#!/usr/bin/env python

from __future__ import print_function
import gammu
import sys
import codecs


def main():
    if len(sys.argv) != 2:
        print('This requires parameter: backup file!')
        sys.exit(1)

    charsetencoder = codecs.getencoder(sys.getdefaultencoding())

    filename = sys.argv[1]

    backup = gammu.ReadSMSBackup(filename)

    # Make nested array
    messages = [[message] for message in backup]

    data = gammu.LinkSMS(messages)

    for message in data:
        decoded = gammu.DecodeSMS(message)

        part = message[0]
        print()
        print('%-15s: %s' % ('Number', part['Number']))
        print('%-15s: %s' % ('Date', str(part['DateTime'])))
        print('%-15s: %s' % ('State', part['State']))
        print('%-15s: %s' % ('Folder', part['Folder']))
        print('%-15s: %s' % ('Validity', part['SMSC']['Validity']))
        loc = []
        for part in message:
            loc.append(str(part['Location']))
        print('%-15s: %s' % ('Location(s)', ', '.join(loc)))
        if decoded is None:
            print('\n%s' % charsetencoder(part['Text'], 'replace')[0])
        else:
            for entries in decoded['Entries']:
                print()
                print('%-15s: %s' % ('Type', entries['ID']))
                if entries['Bitmap'] is not None:
                    for bmp in entries['Bitmap']:
                        print('Bitmap:')
                        for row in bmp['XPM'][3:]:
                            print(row)
                    print()
                if entries['Buffer'] is not None:
                    print('Text:')
                    print(charsetencoder(entries['Buffer'], 'replace'))
                    print()

if __name__ == '__main__':
    main()
