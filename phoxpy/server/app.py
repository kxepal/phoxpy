# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from flask import Flask, request, abort
from phoxpy import xml
from phoxpy import exceptions

app = Flask(__name__)

@app.before_request
def dispatch():
    if request.method == 'GET':
        return

    clength = request.headers['content_length']
    if not clength or clength == '0':
        abort(400, 'payload required')

    try:
        message = xml.decode(request.stream)
    except Exception, err: # don't care about error
        abort(500, str(err))

    if not message.type:
        abort(400, 'message type is missed')

    if not message.sessionid:
        raise exceptions.UnknownSession('session id missed')

    if request.path == '/phox':
        for rule in app.url_map.iter_rules():
            if rule.rule.endswith(message.type):
                request.path = rule.rule
                request.url_rule = rule
                request.phoxmsg = message
                break
        else:
            abort(400, 'unknown type %r' % message.type)
    else:
        abort(404)

@app.route('/phox', methods=['GET','POST'])
def phox():
    return '<h1>It works!</h1>'

@app.errorhandler(exceptions.LisBaseException)
def handle_lis_error(err):
    error = xml.encode(err)
    root = xml.Element('phox-response')
    root.append(error)
    return xml.dump(root)

if __name__ == '__main__':
    app.debug = True
    app.run()
