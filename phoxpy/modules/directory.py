# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy import xml
from phoxpy.messages import PhoxRequest
from phoxpy.mapping import Mapping, ObjectField, ListField, \
                           RefField, TextField, AttributeField


__all__ = ['DirectoryLoad', 'DirectorySave', 'DirectorySaveNew',
           'DirectoryRemove', 'DirectoryRemoveNew', 'DirectoryRestore',
           'load', 'save', 'remove', 'restore',
           'DIRS_FOR_NEW_PROC']

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

class DirectoryRequestNewMixIn(PhoxRequest):
    """MixIn to generate XML output in required format."""
    def unwrap(self):
        root = xml.Element('phox-request')
        content = xml.Element('content')
        obj = xml.Element('o')
        content.append(obj)
        root.append(content)
        return super(PhoxRequest, self).unwrap(root, obj)

    @classmethod
    def wrap(cls, xmlsrc, **defaults):
        defaults.setdefault('type', xmlsrc.attrib['type'])
        defaults.setdefault('sessionid', xmlsrc.attrib.get('sessionid'))
        defaults.setdefault('buildnumber', xmlsrc.attrib.get('buildnumber'))
        defaults.setdefault('version', xmlsrc.attrib.get('version'))
        req = super(PhoxRequest, cls).wrap(xmlsrc.find('content/o'), **defaults)
        return req


class DirectoryLoad(PhoxRequest):
    """Message for request type ``directory``.

    :param name: Directory data source name.
    :type name: str

    :param elements: List of object ids. If None all data will be requests.
    :type elements: list of int
    """
    name = TextField()
    elements = ListField(RefField())

    def __init__(self, name, elements=None, **data):
        data['name'] = name
        if elements is not None:
            data['elements'] = elements
        data['type'] = 'directory'
        super(DirectoryLoad, self).__init__(**data)


class DirectorySave(PhoxRequest):
    """Message for request type ``directory-save``.

    :param directory: Directory data source name.
    :type directory: str

    :param element: Object mapping instance.
    :type element: :class:`~phoxpy.mapping.Mapping`
    """
    directory = TextField()
    element = ObjectField(Mapping.build(id=AttributeField()))

    def __init__(self, directory, element, **data):
        data['directory'] = directory
        if isinstance(element, Mapping):
            element = element.to_python()
        element.pop('removed', None) # This field could be received by .load()
                                     # function, but it shouldn't pass to
                                     # .save() one. Removing it manually is not
                                     # very obliviously.
        data['element'] = element
        data['type'] = 'directory-save'
        super(DirectorySave, self).__init__(**data)


class DirectorySaveNew(DirectoryRequestNewMixIn, DirectorySave):
    """Message for request type ``directory-save-new``.
    Applies to only specific group of directories which are listed in
    :const:`~phoxpy.modules.directory.DIRS_FOR_NEW_PROC`."""
    def __init__(self, *args, **data):
        super(DirectorySaveNew, self).__init__(*args, **data)
        self.type = 'directory-save-new'


class DirectoryRemove(PhoxRequest):
    """Message for request type ``directory-remove``.

    :param directory: Directory data source name.
    :type directory: str

    :param ids: List of object ids.
    :type ids: list
    """
    directory = TextField()
    ids = ListField(RefField())

    def __init__(self, directory, ids, **data):
        data['directory'] = directory
        data['ids'] = ids
        data['type'] = 'directory-remove'
        super(DirectoryRemove, self).__init__(**data)


class DirectoryRemoveNew(DirectoryRequestNewMixIn, DirectoryRemove):
    """Message for request type ``directory-remove-new``.
    Applies to only specific group of directories which are listed in
    :const:`~phoxpy.modules.directory.DIRS_FOR_NEW_PROC`."""
    def __init__(self, *args, **data):
        super(DirectoryRemoveNew, self).__init__(*args, **data)
        self.type = 'directory-remove-new'


class DirectoryRestore(PhoxRequest):
    """Message for request type ``directory-restore``.

    :param directory: Directory data source name.
    :type directory: str

    :param ids: List of object ids.
    :type ids: list
    """
    directory = TextField()
    ids = ListField(RefField())

    def __init__(self, directory, ids, **data):
        data['directory'] = directory
        data['ids'] = ids
        data['type'] = 'directory-restore'
        super(DirectoryRestore, self).__init__(**data)

def maybe_item_or_ids(value):
    """Helper to make no difference what have passed: directory item, single or
    list of ids.
    """
    if isinstance(value, (dict, Mapping)):
        return [value['id']]
    elif isinstance(value, int):
        return [value]
    else:
        return value

def list(session):
    """Iterates over all available directories.

    :param session: Active session instance.
    :type session: :class:`~phoxpy.client.Session`

    :yields: 2-element tuple with directory name and his version.
    """
    resp = session.request(body=PhoxRequest(type='directory-versions'))
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
    resp = session.request(body=DirectoryLoad(name, elements=ids))
    for item in resp[name]:
        yield item.to_python()

def save(session, name, item):
    """Store directory object on server.

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
    message = messagecls(name, item)
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
        message = DirectoryRemoveNew(name, ids)
        resp = session.request(body=message)
        return resp['version']
    else:
        # let's say "thanks" for unstructured answer
        wrapper = lambda el: el.find('content/f').attrib['v']
        resp = session.request(body=DirectoryRemove(name, ids), wrapper=wrapper)
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
    message = DirectoryRestore(name, ids)
    session.request(body=message)
    return True
