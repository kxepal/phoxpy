# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from flask import Flask

app = Flask(__name__)

@app.route('/phox', methods=['GET','POST'])
def phox():
    return '<h1>It works!</h1>'

if __name__ == '__main__':
    app.debug = True
    app.run()
