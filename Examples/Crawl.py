import os


if __name__ == u"__main__":
    path = os.environ[u'HOME'] + os.sep + u"logs"

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            print(u"%s" % os.path.join(root, name))
