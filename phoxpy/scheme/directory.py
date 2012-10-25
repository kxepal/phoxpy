# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from phoxpy.messages import PhoxRequestContent
from phoxpy.mapping import (
    Mapping, ObjectField, ListField, RefField, TextField, AttributeField
)

__all__ = ['DirectoryLoad', 'DirectorySave', 'DirectorySaveNew',
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
