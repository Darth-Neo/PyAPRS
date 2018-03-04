import imp
import inspect
import sys

if len(sys.argv) >= 2:
    filename = sys.argv[1]
else:
    filename = "example.py"

    try:
        (name, suffix, mode, mtype) = inspect.getmoduleinfo(filename)
    except TypeError:
        print("Could not determine module type of %s" % filename)
    else:
        mtype_name = {imp.PY_SOURCE: "source",
                      imp.PY_COMPILED: "compiled",
                      }.get(mtype, mtype)

        mode_description = {"rb": "(read-binary)",
                            "U": "(universal newline)",
                            }.get(mode, "")

        print("NAME   : {}".format(name))
        print("SUFFIX : {}".format(suffix))
        print("MODE   : {} \t {}".format(mode, mode_description))
        print("MTYPE  : {}".format(mtype_name))
