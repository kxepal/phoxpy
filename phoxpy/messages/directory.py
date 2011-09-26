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
           'DirectoryVersions']

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
    def wrap_xmlelem(cls, xmlelem, defaults):
        defaults.update(xmlelem.attrib)
        root = xmlelem.find('content/o')
        assert root is not None
        return super(PhoxRequest, cls).wrap_xmlelem(root, defaults)


class DirectoryLoad(PhoxRequest, 'directory'):
    """Message for request type ``directory``.

    :param name: Directory data source name.
    :type name: str

    :param elements: List of object ids. If None all data will be requests.
    :type elements: list of int
    """
    name = TextField()
    elements = ListField(RefField())


class DirectorySave(PhoxRequest, 'directory-save'):
    """Message for request type ``directory-save``.

    :param directory: Directory data source name.
    :type directory: str

    :param element: Object mapping instance.
    :type element: :class:`~phoxpy.mapping.Mapping`
    """
    directory = TextField()
    element = ObjectField(Mapping.build(id=AttributeField()))


class DirectorySaveNew(DirectoryRequestNewMixIn, DirectorySave,
                       'directory-save-new'):
    """Message for request type ``directory-save-new``.
    Applies to only specific group of directories which are listed in
    :const:`~phoxpy.modules.directory.DIRS_FOR_NEW_PROC`."""


class DirectoryRemove(PhoxRequest, 'directory-remove'):
    """Message for request type ``directory-remove``.

    :param directory: Directory data source name.
    :type directory: str

    :param ids: List of object ids.
    :type ids: list
    """
    directory = TextField()
    ids = ListField(RefField())


class DirectoryRemoveNew(DirectoryRequestNewMixIn, DirectoryRemove,
                         'directory-remove-new'):
    """Message for request type ``directory-remove-new``.
    Applies to only specific group of directories which are listed in
    :const:`~phoxpy.modules.directory.DIRS_FOR_NEW_PROC`."""


class DirectoryRestore(PhoxRequest, 'directory-restore'):
    """Message for request type ``directory-restore``.

    :param directory: Directory data source name.
    :type directory: str

    :param ids: List of object ids.
    :type ids: list
    """
    directory = TextField()
    ids = ListField(RefField())


class DirectoryVersions(PhoxRequest, 'directory-versions'):
    """Message for request type ``directory-versions``."""
