#!/usr/bin/env python
# __author__ = u"james.morris"
import sys


def read_in():
    lines = sys.stdin.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].replace(u"\n", u"")
    # print lines
    return lines


def main():
    lines = read_in()
    print(u"%s" % lines)

if __name__ == u"__main__":
    main()

# sys.stdout
# sys.stdin
