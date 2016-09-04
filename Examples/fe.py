#!/usr/bin/env python
from flask import Flask, make_response
from flask import render_template, request
import datetime
import dateutil.relativedelta

from YAMLQuery import *
from CommonAPI import *

from PyAPRS.rmq.Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

# Note: if the server fails to start, you may be trying to start on a port already in use.

# Globals
app = Flask(__name__)
app.config.from_object(u"config")
vo = VersionOne()
resFile=u"run/pf.p"
TEST = True

# TODO - Make it so you can add or remove queris at will
# TODO - Create script to promote to vicevpsla0021.wdw.disney.com
# TODO - Track all IP's that are using the site
# TODO - Make Blanks be Null
# TODO - Remoce { and }
# TODO - &#39; is apostrophe '
# TODO - Clean Name Field

try:
    import sqlite3

    def logIP(ip):
        conn = sqlite3.connect(u'IP.db')
        c = conn.cursor()
        c.execute(u"insert into ip_log values('now', %s)" %  ip)

except ImportError, msg:
    logger.warn(u"%s" % msg)
    def ip():
        return u""


@app.route("/")
def replyVersionOne():
    global TEST
    title = u"VersionOne Reports"
    templateFile = u"index.html"
    parent = u"Scope:990556"

    methods = vo.method_names

    tday = datetime.datetime.now()
    fday = tday + dateutil.relativedelta.relativedelta(months=-1)

    return render_template(templateFile, title=title, tday=tday, fday=fday, parent=parent,
                           queries=methods, ip=request.remote_addr)


@app.route(u"/query", methods=[u"POST"])
def executeYAML():
    global TEST
    logger.info(u"%s" % __name__)
    templateFile = u"query.html"

    try:
        q = request.form[u"query"].decode(u"utf-8", errors=u"replace")
        query = q.replace("\r", "")
        logger.debug(u"query : %s%s" % (os.linesep, query))

        result = vo.yamlQuery(query)

        if result is not None:
            hl, error = buildHeaders(result)

            return render_template(templateFile, headers=hl, test=TEST, error=error,
                                   query=query, result=result, ip=request.remote_addr)
        else:
            return render_template(templateFile, headers=None, test=TEST, error=u"No result",
                                   query=query, result=None,   ip=request.remote_addr)

    except Exception, msg:
        logger.error(u"%s" % msg)
        return render_template(templateFile, headers=None, test=TEST, error=msg,
                               query=query, result=None, ip=request.remote_addr)


@app.route(u"/gtq", methods=[u"POST"])
def executeReRun():
    global TEST
    logger.info(u"%s" % __name__)
    templateFile = u"query.html"

    pfday = request.form[u"fday"]
    fday = pfday + u"T00:00:00.0000000Z"

    ptday = request.form[u"tday"]
    tday = ptday + u"T00:00:00.0000000Z"

    try:
        query = request.form[u"query"].decode(u"utf-8", errors=u"replace")
        fileQuery = u"query%s" % query
        payload, result = getattr(vo, fileQuery)(fday=fday, tday=tday)

        if TEST is True:
            dumpPickle(result)

        if result is not None:
            hl, error = buildHeaders(result)

            return render_template(templateFile, tday=ptday, fday=pfday, headers=hl, test=TEST, error=error,
                                   query=payload, result=result)
        else:
            return render_template(templateFile, tday=ptday, fday=pfday, headers=None, test=TEST, error=None,
                                   query=payload, result=None)

    except Exception, msg:
        logger.error(u"%s" % msg)
        return render_template(templateFile, tday=ptday, fday=pfday, headers=None, test=TEST, error=msg,
                               query=query, r0=None, result=None)


@app.route(u"/download", methods=[u"POST"])
def _download():
    logger.info(u"%s" % __name__)
    templateFile = u"query.html"

    q = request.form[u"query"].decode(u"utf-8", errors=u"replace")
    query = q.replace("\r", "")
    logger.debug(u"query : %s%s" % (os.linesep, query))

    result_output = request.form[u"ro"].decode(u"utf-8", errors=u"replace")

    try:
        response = make_response(result_output)
        response.headers[u"Content-Disposition"] = u"attachment; filename=query.csv"
        return response

    except Exception, msg :
        error = u"Invalid Entry, please try again"
        return render_template(templateFile, error=error, result=None)

@app.route(u"/test", methods=[u"get"])
def test_page():
    global TEST
    templateFile = u"test.html"

    try:
        result = loadPickle()

        if result is not None:
            hl, error = buildHeaders(result)

            return render_template(templateFile, headers=hl, test=TEST, error=error,
                                   result=result, ip=request.remote_addr)
        else:
            return render_template(templateFile, headers=None, test=TEST, error=u"No result",
                                   result=None,   ip=request.remote_addr)

    except Exception, msg :
        error = u"Invalid Entry, please try again"
        return render_template(templateFile, test=TEST, error=error, result=None)

@app.errorhandler(500)
def server_error(e):
    error = u"Server Error, please try again"
    return render_template(u"index.html", error=error)

@app.errorhandler(404)
def page_not_found(e):
    error = u"File not found, please try again"
    return render_template(u"index.html", error=error)

if __name__ == u"__main__":
    configFile = u"versionone.conf"
    Config = ConfigParser.ConfigParser()
    Config.read(configFile)

    nem = ConfigSectionMap(u"Server", Config)[u'noerrormsg']
    if  nem == u"True":
        noErrorMsg()

    dsc = ConfigSectionMap(u"Server", Config)[u'disablesslcheck']
    if  dsc == u"True":
        disableSSLCheck()

    host = ConfigSectionMap(u"Server", Config)[u'host']
    port = int(ConfigSectionMap(u"Server", Config)[u'port'])
    app.run(debug=True, host=host, port=port)

    pass