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
           'DirectoryRemove', 'DirectoryRemoveNew', 'DirectoryRestore']

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


class DirectoryVersions(PhoxRequest):
    """Message for request type ``directory-versions``."""
    directory = TextField()
    ids = ListField(RefField())

    def __init__(self, **data):
        data['type'] = 'directory-versions'
        super(DirectoryVersions, self).__init__(**data)
