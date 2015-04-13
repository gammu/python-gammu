#!/usr/bin/env python

from __future__ import print_function
import gammu.exception


def main():
    for exc in sorted(gammu.exception.__all__):
        print('.. exception:: gammu.{0}'.format(exc))
        print()
        doc = getattr(gammu.exception, exc).__doc__
        for doc in doc.splitlines():
            print('    {0}'.format(doc))
        print()


if __name__ == '__main__':
    main()
