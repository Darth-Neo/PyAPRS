#!/usr/bin/env python
import os
import sys
import time

if __name__ == u"__main__":
    sys.stdout.write(u"Here we go...%s" % os.linesep)
    sys.stdout.flush()

    try:
        while True:
            l1 = sys.stdin.readline()
            l2 = sys.stdin.readline()

            sys.stdout.write(u"l [%s] %s" % (l1, os.linesep))
            sys.stdout.flush()

            if len(l1) == 0:
                sys.stdout.write(u"All caught up.%s" % os.linesep)
                sys.stdout.flush()
            else:
                sys.stdout.write(u"Read %d letters %s" % (len(l1), os.linesep))
                sys.stdout.flush()

                time.sleep(2)

    except KeyboardInterrupt:
        sys.stdout.write(u"TTFN%s" % os.linesep)
        sys.stdout.flush()
        sys.exit(0)