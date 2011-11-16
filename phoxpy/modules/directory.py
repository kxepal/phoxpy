# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.mapping import Mapping
from phoxpy.messages.directory import \
    DirectoryLoad, DirectorySave, DirectorySaveNew, \
    DirectoryRemove, DirectoryRemoveNew, DirectoryRestore, \
    DirectoryVersions

__all__ = ['DIRS_FOR_NEW_PROC', 'items', 'load', 'store', 'remove', 'restore']

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
    resp = session.request(body=DirectoryVersions())
    for db in resp['versions']:
        yield db['name'], db['version']

def load(session, name, ids=None):
    """Loads data from specified directory.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :param name: Directory name.
    :type name: str

    :param ids: List of object ids. If omitted, all objects will be loaded.
    :type ids: list

    :yields: Directory objects as dict.
    """
    ids = maybe_item_or_ids(ids)
    resp = session.request(body=DirectoryLoad(name=name, elements=ids))
    for item in resp[name]:
        yield item.unwrap()

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
        messagecls = DirectorySaveNew
    else:
        messagecls = DirectorySave
    if isinstance(item, Mapping):
        item = item.unwrap()
    item.pop('removed', None) # This field could be received by .load()
                              # function, but it shouldn't pass to
                              # .save() one. Removing it manually is not
                              # very obliviously.
    message = messagecls(directory=name, element=item)
    resp = session.request(body=message)
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
    if name in DIRS_FOR_NEW_PROC:
        message = DirectoryRemoveNew(directory=name, ids=ids)
        resp = session.request(body=message)
        return resp['version']
    else:
        message = DirectoryRemove(directory=name, ids=ids)
        # let's say "thanks" for unstructured answer
        def wrapper(stream):
            stream.next() # phox-response
            stream.next() # content
            event, elem = stream.next()
            assert event == 'start' and elem.tag == 'f'
            version = int(elem.attrib['v'])
            for item in stream: # cleanup
                pass
            return version
        resp = session.request(body=message, wrapper=wrapper)
        return resp

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
