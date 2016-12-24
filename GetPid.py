#!/usr/bin/env python
import sys
import os
import psutil
import subprocess
from subprocess import check_output, CalledProcessError

from Logger import *

logger = setupLogging(__name__)
logger.setLevel(DEBUG)


def getPIDs(process):
    try:
        pidlist = map(int, check_output([u"pidof", process]).split())

    except  CalledProcessError:
        pidlist = []

    logger.debug(u"list of PIDs = " + u", ".join(str(e) for e in pidlist))


def getPID(find_proc_name):
    process_found = False
    Use_SUDO = True
    pid = None
    sp = None

    # check whether the process name matches
    for proc in psutil.process_iter():
        name = proc.name
        pid = proc.pid
        cmdline = u"/proc/{}/cmdline".format(pid)

        p = subprocess.Popen([u"/bin/ps", u"-f"], stdout=subprocess.PIPE)
        owner = p.stdout.read()
        # logger.debug(u"Owner : {}".format(owner))

        if Use_SUDO is True:
            sp = subprocess.check_output([u"sudo", u"cat", cmdline])
        else:
            sp = subprocess.check_output([u"cat", cmdline])

        if len(sp) <> 0 and find_proc_name in sp:
            logger.debug(u"PID {:5} : ..{}..".format(pid, sp))
            process_found = True
            break

            # proc.kill()

            # output = Popen(["cat", cmdline], stdout=subprocess.PIPE)
            # proc.wait()

            # proc = Popen(["pkill", "-f", name], stdout=subprocess.PIPE)
            # proc.wait()

    return process_found, pid, sp

if __name__ == u"__main__":

    logger.debug(u"Number of arguments: {} arguments.".format(len(sys.argv)))
    logger.debug(u"Argument List:i {}".format(str(sys.argv)))

    if len(sys.argv) > 1:
        find_proc_name = sys.argv[1]
    else:
        find_proc_name = u"mongod"

    logger.debug(u"Find: {}".format(find_proc_name))

    process_found, pid, sp = getPID(find_proc_name)
