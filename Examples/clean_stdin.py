#!/usr/bin/env python
import os
import sys
import time

if __name__ == u"__main__":
    sys.stdout.write(u"Here we go...")
    sys.stdout.flush()

    while True:
        try:
            l = sys.stdin.readline()

            sys.stdout.write(u"l [%s] %s" % (l, os.linesep))
            sys.stdout.flush()

            if len(l) == 0:
                sys.stdout.write(u"All caught up.%s" % os.linesep)
                sys.stdout.flush()
            else:
                sys.stdout.write(u"Read %d lines %s" % (len(l), os.linesep))
                sys.stdout.flush()

                time.sleep(10)

        except KeyboardInterrupt:
            sys.stdout.write(u"TTFN%s" % os.linesep)
            sys.stdout.flush()
            sys.exit(0)