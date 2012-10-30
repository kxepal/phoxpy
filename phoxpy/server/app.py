# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from flask import Flask, Response, abort, request
from phoxpy import xml
from phoxpy import exceptions
from phoxpy.messages import PhoxRequest, PhoxResponse, PhoxEvent

app = Flask(__name__)

def dispatch_phox_request(message):
    if message.type == 'login':
        raise exceptions.NoContentHandlerError(message.type)

    if message.sessionid is None:
        raise exceptions.NotAuthorized('session id missed')

    raise exceptions.NoContentHandlerError(message.type)

def dispatch(message):
    if isinstance(message, PhoxRequest):
        return dispatch_phox_request(message)
    elif isinstance(message, PhoxEvent):
        raise exceptions.RequestParsingError('not implemented')
    else:
        raise exceptions.RequestParsingError('unknown message')

@app.route('/phox', methods=['GET', 'POST'])
def phox():
    if request.method == 'GET':
        return '<h1>It works!</h1>'

    try:
        message = xml.decode(request.stream)
    except Exception:
        abort(400)

    if not message.type:
        abort(400)

    response = dispatch(message)

    response['sessionid'] = message.sessionid

    return Response(str(PhoxResponse(**response)), mimetype='application/xml')


@app.errorhandler(exceptions.LisBaseException)
def handle_lis_error(err):
    error = xml.encode(err)
    root = xml.Element('phox-response')
    root.append(error)
    return xml.dump(root)

if __name__ == '__main__':
    app.debug = True
    app.run()
