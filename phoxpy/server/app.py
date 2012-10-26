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

app = Flask(__name__)

@app.before_request
def dispatch():
    if not request.headers['content_length']:
        abort(400, 'payload required')
    message = xml.decode(request.stream)
    if message.type is None:
        abort(400, 'message type is missed')
    elif request.path == '/phox':
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

if __name__ == '__main__':
    app.debug = True
    app.run()
