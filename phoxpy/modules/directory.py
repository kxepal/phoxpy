# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import time
from phoxpy.xmlcodec import DirectoryResponseCodec
from phoxpy.mapping import (
    Mapping, ObjectField, ListField, RefField, TextField, AttributeField
)
from phoxpy.messages import PhoxRequest, PhoxRequestContent

__all__ = ['DIRS_FOR_NEW_PROC',
           'items', 'load', 'store', 'remove', 'restore',
           'DirectoryLoad', 'DirectorySave', 'DirectorySaveNew',
           'DirectoryRemove', 'DirectoryRemoveNew', 'DirectoryRestore']

class DirectoryLoad(PhoxRequestContent):
    """Content for request type ``directory``."""

    #: Directory data source name.
    name = TextField()
    #: List of object ids. If None all of them will be requests.
    elements = ListField(RefField())


class DirectorySave(PhoxRequestContent):
    """Content for request type ``directory-save``."""

    #: Directory data source name.
    directory = TextField()
    #: Directory element to save.
    element = ObjectField(Mapping.build(id=AttributeField()))


class DirectoryRemove(PhoxRequestContent):
    """Content for request type ``directory-remove``."""

    #: Directory data source name.
    directory = TextField()
    #: List of object ids to remove.
    ids = ListField(RefField())


class DirectoryRestore(PhoxRequestContent):
    """Content for request type ``directory-restore``."""

    #: Directory data source name.
    directory = TextField()
    #: List of object ids to restore.
    ids = ListField(RefField())


#: List of directory names to which new directory message format should be
#: applied.
DIRS_FOR_NEW_PROC = set(
    ['constant', 'containerGroup', 'containerType', 'courier', 'customCommand',
     'customReport', 'defectType', 'directoryTree', 'employee',
     'hospitalCategory', 'incomingMaterialType', 'myelogramm', 'outsourcer',
     'plateAlgorithm', 'printFormHeader', 'printFormUnit', 'qcAnalyte',
     'qcEvent', 'qcMaterial', 'qcPointComment', 'qcProducer', 'qcTestGroup',
     'requestCustomState', 'sampleBlank', 'userGraphics', 'userGraphicsElement',
     'wellType', 'worklistDefGroup']
)

def maybe_item_or_ids(value):
    """Helper to make no difference what have passed: directory item, single or
    list of ids.
    """
    if isinstance(value, (dict, Mapping)):
        return [value['id']]
    elif isinstance(value, list):
        return value
    elif value is not None:
        return [value]

def items(session):
    """Iterates over all available directories.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :yields: 2-element tuple with directory name and his version.
    """
    resp = session.request(body=PhoxRequest(type='directory-versions'))
    for db in resp['versions']:
        yield db['name'], db['version']

def load(session, name, ids=None, removed=False, _wrapper=DirectoryResponseCodec):
    """Loads data from specified directory.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param name: Directory name.
    :type name: str

    :param ids: List of object ids. If omitted, all objects will be loaded.
    :type ids: list

    :param removed: Allows to yield removed items if set as True.
    :type removed: bool

    :yields: Directory objects as dict.
    """
    ids = maybe_item_or_ids(ids)
    msg = DirectoryLoad(name=name, elements=ids).to_message(type='directory')
    resp = session.request(body=msg, wrapper=_wrapper)
    for item in resp[name]:
        if not removed and item.get('removed', False):
            continue
        yield item

def store(session, name, item):
    """Stores directory object on server.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param name: Directory name.
    :type name: str

    :param item: Directory object. If it has not `id` key new object will be
                 created.
    :type item: dict or :class:`~phoxpy.mapping.Mapping` instance

    :returns: Object id and new directory version.
    :rtype: tuple
    """
    if name in DIRS_FOR_NEW_PROC:
        msgtype = 'directory-save-new'
    else:
        msgtype = 'directory-save'
    if isinstance(item, Mapping):
        item = item.unwrap()
    item.pop('removed', None) # This field could be received by .load()
                              # function, but it shouldn't pass to
                              # .store() one. Removing it manually is not
                              # very obliviously.
    msg = DirectorySave(directory=name, element=item).to_message(type=msgtype)
    resp = session.request(body=msg)
    item['id'] = resp['id']
    return item['id'], resp['version']

def remove(session, name, ids):
    """Marks directory objects as removed. This is not actual removing, but
    hiding objects from user sight.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param name: Directory name.
    :type name: str

    :param ids: List of object ids to remove.
    :type ids: list

    :returns: New directory version.
    :rtype: str
    """
    ids = maybe_item_or_ids(ids)
    content = DirectoryRemove(directory=name, ids=ids)
    if name in DIRS_FOR_NEW_PROC:
        msg = content.to_message(type='directory-remove-new')
        resp = session.request(body=msg)
        return resp.content['version']
    else:
        msg = content.to_message(type='directory-remove')
        resp = session.request(body=msg)
        return resp['version']

def restore(session, name, ids):
    """Restores removed directory objects.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param name: Directory name.
    :type name: str

    :param ids: List of object ids to restore.
    :type ids: list

    :returns: True
    :rtype: bool
    """
    ids = maybe_item_or_ids(ids)
    message = DirectoryRestore(directory=name, ids=ids)
    session.request(body=message)
    return True

def changes(session, init_versions=None, timeout=10):
    """Setups infinity changes feed in all or specified directories.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param init_versions: Initial mapping of directory names to their versions.
                          If omitted, all directories will be listening.
    :type init_versions: dict

    :param timeout: Timeout between directory-version requests.
                    Default is 10 sec.
    :type timeout: int

    :yields: 2-element tuple with directory name and his new version.
    """
    versions = init_versions or {}
    if not versions:
        for name, version in items(session):
            versions[name] = version
            yield name, version
    while True:
        for name, version in items(session):
            if name in versions and versions[name] < version:
                yield name, version
                versions[name] = version
        time.sleep(timeout)
