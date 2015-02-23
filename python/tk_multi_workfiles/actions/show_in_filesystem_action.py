# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
"""

import sgtk

from .file_action import FileAction

import os
import sys
from itertools import chain

class ShowInFileSystemAction(FileAction):
    """
    """
    def _show_in_fs(self, path):
        """
        """
        # find the deepest path that actually exists:
        while path and not os.path.exists(path):
            path = os.path.dirname(path)
        if not path:
            return
        
        # ensure the slashes are correct:
        path = path.replace("/", os.path.sep)
        
        # build the command:
        if sys.platform == "linux2":
            # TODO - figure out how to open the parent and select the file/path
            if os.path.isfile(path):
                path = os.path.dirname(path)
            cmd = "xdg-open \"%s\"" % path
        elif sys.platform.startswith("darwin"):
            cmd = "open -R \"%s\"" % path
        elif sys.platform == "win32":
            # TODO - figure out how to open the parent and select the file/path
            if os.path.isfile(path):
                path = os.path.dirname(path)
            cmd = "cmd.exe /C start \"Folder\" \"%s\"" % path
        else:
            raise TankError("Platform '%s' is not supported." % system)
        
        # run the command:
        exit_code = os.system(cmd)
        if exit_code != 0:
            self._app.log_error("Failed to launch '%s'!" % cmd)
    
class ShowPublishInFileSystemAction(ShowInFileSystemAction):
    """
    """
    def __init__(self):
        ShowInFileSystemAction.__init__(self, "Show Publish In File System")
        
    def execute(self, file, file_versions, environment, parent_ui):
        """
        """
        if file and file.is_published:
            self._show_in_fs(file.publish_path)
    
class ShowWorkFileInFileSystemAction(ShowInFileSystemAction):
    """
    """
    def __init__(self):
        ShowInFileSystemAction.__init__(self, "Show Work File In File System")
        
    def execute(self, file, file_versions, environment, parent_ui):
        """
        """
        if file and file.is_local:
            self._show_in_fs(file.path)

class ShowAreaInFileSystemAction(ShowInFileSystemAction):
    def _show_area_in_fs(self, file, template):
        """
        """
        # build fields starting with the context:
        fields = environment.context.as_template_fields(template)
        if file:
            # add any additional fields that we can extract from the work or publish paths
            file_fields = {}
            if file.is_local and environment.work_template:
                try:
                    file_fields = environment.work_template.get_fields(file.path)
                except TankError, e:
                    pass
            elif file.is_published and environment.publish_template:
                try:
                    file_fields = environment.publish_template.get_fields(file.publish_path)
                except TankError, e:
                    pass
            # combine with the context fields, preferring the context
            fields = dict(chain(ctx_fields.iteritems(), file_fields.iteritems()))
            
        # try to build a path from the template with these fields:
        while template and template.missing_keys(fields):
            template = template.parent
        if not template:
            # failed to find a template with no missing keys!
            return
        path = template.apply_fields(fields)
        
        # finally, show the path:
        self._show_in_fs(path)

class ShowWorkAreaInFileSystemAction(ShowInFileSystemAction):
    """
    """
    def __init__(self):
        ShowInFileSystemAction.__init__(self, "Show Work Area In File System")
        
    def execute(self, file, file_versions, environment, parent_ui):
        """
        """
        if not file:
            return
        
        if not environment or not environment.context or not environment.work_area_template:
            return

        self._show_area_in_fs(file, environment.work_area_template)

class ShowPublishAreaInFileSystemAction(ShowInFileSystemAction):
    """
    """
    def __init__(self):
        ShowInFileSystemAction.__init__(self, "Show Publish Area In File System")
        
    def execute(self, file, file_versions, environment, parent_ui):
        """
        """
        if not file:
            return
        
        if not environment or not environment.context or not environment.publish_area_template:
            return
        
        self._show_area_in_fs(file, environment.publish_area_template)
        