# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import time
from phoxpy.messages import PhoxRequest
from phoxpy.scheme.requests import RequestInfo, RequestSamples


__all__ = ['load', 'select', 'changes', 'samples']


def load(session, idx):
    """Loads request information by provided id.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param idx: Request id.
    :type idx: str

    :returns: Request information.
    :rtype: dict
    """
    msg = RequestInfo(request=idx).to_message(type='request-info')
    resp = session.request(body=msg)
    data = resp.unwrap()
    data.pop('sessionid', None)
    data.pop('buildnumber', None)
    return data

def select(session, filter=None, **options):
    """Selects requests from registration journal.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param filter: Predefined requests filter.
    :type filter: :class:`~phoxpy.modules.requests.RegistrationJournalFilter`

    :param options: Custom additional filter options. See
                    :class:`~phoxpy.modules.requests.RegistrationJournalFilter`
                    for supported keys.

    :yields: Registration journal rows.
    :rtype: dict
    """
    if filter is None:
        filter = RegistrationJournalFilter(**options)
    else:
        filter.update(options)
    msg = RegistrationJournal(filter=filter).to_message(type='registration-journal')
    resp = session.request(body=msg)
    for row in resp['Request']:
        yield row

def samples(session, idx):
    """Retrieves short information about request samples.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param idx: Request id.
    :type idx: str

    :yields: Information about samples.
    :rtype: dict
    """
    msg = RequestSamples(request=idx).to_message(type='request-samples')
    resp = session.request(body=msg)
    for sample in resp['samples']:
        yield sample

def changes(session,  timestamp=0, timeout=10):
    """Generates changes in registration journal since specified timestamp.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param timestamp: Prepared requests filter.
    :type timestamp: int

    :param timeout: Timeout between directory-version requests.
                    Default is 10 sec.
    :type timeout: int

    :yields: Registration journal rows as dict.
    """
    while True:
        for item in select(session, last_timestamp=timestamp):
            if timestamp < item['timestamp']:
                timestamp = item['timestamp']
                yield item
        time.sleep(timeout)
