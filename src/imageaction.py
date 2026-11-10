#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#This file is part of PyFuriusIsoMount. Copyright 2008 Dean Harris (marcus_furius@hotmail.com)
#
#    PyFuriusIsoMount is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFuriusIsoMount is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFuriusIsoMount.  If not, see <http://www.gnu.org/licenses/>.

import os
import shlex
import globals
import log
import subprocess
from configparser import ConfigParser
from gettext import gettext as _

def mount(image_file, is_fuse):
    """Mount image_file and return the mount_location it was mounted at. Raises on failure."""
    image_name = os.path.basename(image_file)

    #Get the mount root point
    config = ConfigParser()
    try:
        config.read(globals.settings_file)
        mount_root = config.get("mount_options", "mount_point")
    except Exception as e:
        log.write(globals.mount_log, _('Error reading mount point setting.\nUnexpected error: %s' % (e)))
        log.write(globals.mount_log, _('Defaulting to home directory for mounting.'))
        mount_root = globals.home_directory
    #Replace any characters that could screw up the new directory's name.
    safe_name = image_name.replace(' ', '_').replace('.', '_')
    mount_location = os.path.join(mount_root, safe_name)

    try:
        # If an image is already mounted this will throw an OSError
        if os.path.exists(mount_location):
            os.rmdir(mount_location)
        os.mkdir(mount_location)

        if is_fuse:
            mount_args = ['fuseiso', image_file, mount_location]
            unmount_hint = 'fusermount -u %s' % shlex.quote(mount_location)
        else: #loop back
            mount_args = ['pkexec', 'mount', '-t', 'auto', '-o', 'loop', image_file, mount_location]
            unmount_hint = 'pkexec umount %s' % shlex.quote(mount_location)

        #Mount the image, writing the executed command to the log
        log.write(globals.mount_log, shlex.join(mount_args))
        returncode = subprocess.Popen(mount_args).wait()
        if returncode != 0:
            raise RuntimeError(_('Mount command exited with status %s.') % returncode)

        #Write an entry with instructions on how to remove manually if needed
        log.write(globals.mount_log,
                  _('%s successfully mounted @ %s. If required, run the following commands to remove:\n  :%s\n  :rmdir %s'
                    % (image_file, mount_location, unmount_hint, mount_location)))
        return mount_location
    except OSError as e:
        log.write(globals.mount_log, _('Error mounting image.\nOS error: %s' % (e)))
        raise
    except Exception as e:
        log.write(globals.mount_log, _('Error mounting image.\nUnexpected error: %s' % (e)))
        raise


def add_item_to_history(image_file, history_array):
    """Insert image_file at the front of history_array (deduping and capping its length), and persist it to disk."""
    # If the image already exists in the list, remove it. We'll be adding it
    # to the top of the list.
    if image_file in history_array:
        history_array.remove(image_file)
    # Add the image to the top
    history_array.insert(0, image_file)
    # If we've hit our history length max drop the last entry
    if len(history_array) > 10:
        del history_array[10]
    # Persist the history to disk
    try:
        with open(globals.history_list, 'w') as history_file:
            for string in history_array:
                history_file.write('%s\n' %(string))
    except OSError as e:
        log.write(globals.mount_log, _('Error saving history to file.\nOS error: %s' % (e)))
        raise
    except Exception as e:
        log.write(globals.mount_log, _('Error saving history to file\nUnexpected error: %s' % (e)))
        raise

def unmount(mount_location, is_mounted_image_fuse):
    """Unmount mount_location. Raises on failure."""
    try:
        # If the directory doesn't exist, it may have been unmounted externally already.
        if os.path.exists(mount_location):
            if is_mounted_image_fuse == 'True':
                unmount_args = ['fusermount', '-u', mount_location]
            else:
                unmount_args = ['pkexec', 'umount', mount_location]
            log.write(globals.mount_log, shlex.join(unmount_args))
            returncode = subprocess.Popen(unmount_args).wait()
            if returncode != 0:
                raise RuntimeError(_('Unmount command exited with status %s.') % returncode)
            os.rmdir(mount_location)
        log.write(globals.mount_log, _('%s successfully unmounted.'%(mount_location)))
    except Exception as e:
        log.write(globals.mount_log, _('Error unmounting image.\nUnexpected error: %s' % (e)))
        raise

def burn(image_file):
    try:
        burn_args = ['brasero', '--image', image_file]
        subprocess.Popen(burn_args)
        log.write(globals.mount_log, shlex.join(burn_args))
    except Exception as e:
        log.write(globals.mount_log, _('Error burning image.\nUnexpected error: %s' % (e)))
        raise

def browse(mount_location):
    try:
        if os.path.exists(mount_location):
            browse_args = ['nautilus', '--browser', mount_location]
            subprocess.Popen(browse_args)
            log.write(globals.mount_log, shlex.join(browse_args))
    except Exception as e:
        log.write(globals.mount_log, _('Error launching nautilus.\nUnexpected error: %s' % (e)))
        raise
