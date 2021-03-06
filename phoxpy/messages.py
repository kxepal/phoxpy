# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import xml
from phoxpy.mapping import MetaMapping, Mapping, AttributeField, ObjectField

__all__ = ['Message', 'PhoxRequest', 'PhoxResponse', 'Content']


class Content(Mapping):
    """Abstract phox message content holder mapping."""

    #: Related :class:`~phox.messages.Message` class.
    phox_message_cls = None

    def to_message(self, **params):
        """Wraps content to related :class:`~phox.messages.Message` defined
        at :class:`~phox.messages.Content.phox_message_cls` attribute.

        :param params: Custom message initialization params.

        :return: :class:`~phox.messages.Content.phox_message_cls` instance.
        """
        msg = self.phox_message_cls(**params)
        msg.content = self
        return msg


class Message(Mapping):
    """Base communication message mapping."""

    #: Unique session id. Sets automatically after successful auth.
    sessionid = AttributeField()
    #: Actual message content holder.
    content = ObjectField(Content)

    def __str__(self):
        raise NotImplementedError('Should be implemented for each message type')

    def __getitem__(self, item):
        if item in self.content:
            return self.content[item]
        return super(Message, self).__getitem__(item)

    def __setitem__(self, key, value):
        if key in self.content:
            self.content[key] = value
        else:
            super(Message, self).__setitem__(key, value)

    def __delitem__(self, key):
        if key in self.content:
            del self.content[key]
        else:
            super(Message, self).__delitem__(key)


class MetaPhoxRequest(MetaMapping):

    def __new__(mcs, name, bases, data):
        reqtype = None
        bases = list(bases)
        for idx, base in enumerate(bases):
            if isinstance(base, str):
                reqtype = bases.pop(idx)
                break
        data['_request_type'] = reqtype
        return super(MetaPhoxRequest, mcs).__new__(mcs, name, tuple(bases), data)

    def __call__(cls, *args, **data):
        if cls._request_type is not None:
            data['type'] = cls._request_type
        content = {}
        for key in list(data):
            if key not in cls._fields:
                content[key] = data.pop(key)
        data['content'] = content
        return super(MetaPhoxRequest, cls).__call__(*args, **data)


class PhoxRequest(Message):
    """Base request message."""
    __metaclass__ = MetaPhoxRequest

    #: Request type.
    type = AttributeField()
    #: Build number. Should be same as server one.
    buildnumber = AttributeField()
    #: Server version.
    version = AttributeField()

    def __init__(self, **kwargs):
        super(PhoxRequest, self).__init__(**kwargs)
        assert self.type is not None

    def __str__(self):
        doctype = ('phox-request', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.to_xml(), doctype=doctype)


class PhoxResponse(Message):
    """Base phox response message. Used as answer on phox requests messages."""
    __metaclass__ = MetaPhoxRequest

    #: Server build number.
    buildnumber = AttributeField()

    def __str__(self):
        doctype = ('phox-response', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.to_xml(), doctype=doctype)

    def unwrap(self):
        resp = super(PhoxResponse, self).unwrap()
        for key in [None, 'content']:
            if key in resp:
                return resp[key].unwrap()
        raise ValueError('unknown content wrapper for response\n%s' % resp)


class PhoxEvent(Message):
    """Base phox event message."""
    __metaclass__ = MetaPhoxRequest

    #: Event source.
    system = AttributeField()
    #: Event type.
    type = AttributeField()

    def __init__(self, **kwargs):
        super(PhoxEvent, self).__init__(**kwargs)
        assert self.type is not None

    def __str__(self):
        doctype = ('phox-event', 'SYSTEM', 'phox.dtd')
        return xml.dump(self.to_xml(), doctype=doctype)


class MessageContent(Mapping):
    """:class:`~phox.messages.Message` content holder mapping."""
    phox_message_cls = Message

class PhoxRequestContent(Content):
    """:class:`~phox.messages.PhoxRequest` content holder mapping."""
    phox_message_cls = PhoxRequest


class PhoxResponseContent(Content):
    """:class:`~phox.messages.PhoxResponse` content holder mapping."""
    phox_message_cls = PhoxResponse
