# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.messages import PhoxRequest
from phoxpy.mapping import Mapping, ObjectField, ListField, \
                           RefField, TextField, AttributeField

__all__ = ['DirectoryLoad', 'DirectorySave', 'DirectorySaveNew',
           'DirectoryRemove', 'DirectoryRemoveNew', 'DirectoryRestore',
           'DirectoryVersions']

class DirectoryLoad(PhoxRequest, 'directory'):
    """Message for request type ``directory``."""
    #: Directory data source name.
    name = TextField()
    #: List of object ids. If None all of them will be requests.
    elements = ListField(RefField())


class DirectorySave(PhoxRequest, 'directory-save'):
    """Message for request type ``directory-save``."""
    #: Directory data source name.
    directory = TextField()
    #: Directory element to save.
    element = ObjectField(Mapping.build(id=AttributeField()))


class DirectorySaveNew(DirectorySave,'directory-save-new'):
    """Message for request type ``directory-save-new``.
    Applies to only specific group of directories which are listed in
    :const:`~phoxpy.modules.directory.DIRS_FOR_NEW_PROC`."""


class DirectoryRemove(PhoxRequest, 'directory-remove'):
    """Message for request type ``directory-remove``."""
    #: Directory data source name.
    directory = TextField()
    #: List of object ids to remove.
    ids = ListField(RefField())


class DirectoryRemoveNew(DirectoryRemove, 'directory-remove-new'):
    """Message for request type ``directory-remove-new``.
    Applies to only specific group of directories which are listed in
    :const:`~phoxpy.modules.directory.DIRS_FOR_NEW_PROC`."""


class DirectoryRestore(PhoxRequest, 'directory-restore'):
    """Message for request type ``directory-restore``."""
    #: Directory data source name.
    directory = TextField()
    #: List of object ids to restore.
    ids = ListField(RefField())


class DirectoryVersions(PhoxRequest, 'directory-versions'):
    """Message for request type ``directory-versions``."""
