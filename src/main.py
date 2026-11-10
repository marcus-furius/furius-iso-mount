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

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import globals
import filehash
import threading
import messagebox
import aboutbox
import locale
import log
import os
import subprocess
import imageaction
import gettext
from gettext import gettext as _


class main_window:
    drop_targets = [Gtk.TargetEntry.new('text/plain', 0, 3)]
    def __init__(self, parameter):

        # Localization
        locale.setlocale(locale.LC_ALL, '')
        gettext.textdomain(globals.assembly_name)
        gettext.bindtextdomain(globals.assembly_name, globals.locale_directory)

        #Set the Glade file
        self.interface = Gtk.Builder()
        self.interface.add_from_file(globals.application_interface)
        self.register_small_font_css()
        self.create_settings_directory()
        self.create_settings_file()
        log.write(globals.mount_log, _('Application started...'))
        self.set_storage_lists()
        self.set_history_entry()
        self.set_mounted_image_treeview()
        self.set_icons_and_text()
        self.load_mount_history()
        self.load_previously_mounted_images()

        HANDLERS_AND_METHODS = {
            'button_checksum_clicked': self.button_checksum_clicked,
            'button_browse_clicked': self.button_browse_clicked,
            'button_about_clicked': self.button_about_clicked,
            'button_view_log_clicked': self.button_view_log_clicked,
            'button_delete_log_clicked': self.button_delete_log_clicked,
            'button_mount_clicked': self.button_mount_clicked,
            'comboentry_image_changed': self.comboentry_image_changed,
            'treeview_mounted_images_cursor_changed': self.treeview_mounted_images_cursor_changed,
            'button_unmount_clicked': self.button_unmount_clicked,
            'button_burn_clicked': self.button_burn_clicked,
            'treeview_mounted_images_drag_data_recieved': self.treeview_mounted_images_drag_data_recieved,
            'treeview_mounted_images_row_activated': self.treeview_mounted_images_row_activated,
            'destroy': self.destroy}
        self.interface.connect_signals(HANDLERS_AND_METHODS)
        # The combo box's entry child isn't addressable from the .glade file, so wire it up here.
        self.interface.get_object('comboentry_image').get_child().connect(
            'key-release-event', self.comboentry_image_key_release)
        if (parameter != ''):
            try:
                self.mount_image(parameter)
            except OSError as e:
                messagebox.show(self.interface.get_object('main_window'), _('Error mounting image.\nOS error(%s): %s') % (e.errno, e.strerror), Gtk.MessageType.ERROR)
            except Exception as e:
                messagebox.show(self.interface.get_object('main_window'), _('Error mounting image.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def mount_image(self, image_file):
        """Mount image_file and update the UI storage/history to reflect it. Raises on failure."""
        is_fuse = self.interface.get_object('radiobutton_fuse').get_active()
        mount_location = imageaction.mount(image_file, is_fuse)
        self.image_storage.append([mount_location, image_file, str(is_fuse)])
        imageaction.add_item_to_history(image_file, self.history_array)
        self.refresh_history_storage()

    def refresh_history_storage(self):
        self.history_storage.clear()
        for entry in self.history_array:
            self.history_storage.append([entry])

    def load_previously_mounted_images(self):
        if os.path.exists(globals.mount_list):
            try:
                with open(globals.mount_list, 'r') as file_previous_images:
                    previous_image_history = file_previous_images.readlines()
                for line in previous_image_history:
                    previous_image = line.strip().split(',')
                    self.image_storage.append([previous_image[0], previous_image[1], previous_image[2]])
                os.remove(globals.mount_list)
            except OSError as e:
                log.write(globals.mount_log, _('Error loading history.\nOS error(%s): %s') % (e.errno, e.strerror))
            except Exception as e:
                log.write(globals.mount_log, _('Error loading history.\nUnexpected error: %s') % (e))

    def load_mount_history(self):
        self.history_array = []
        #Load the history
        if os.path.exists(globals.history_list):
            try:
                with open(globals.history_list, 'r') as file_history:
                    self.mount_history = file_history.readlines()
                for line in self.mount_history:
                    self.history_array.append(line.strip())
                self.refresh_history_storage()
            except OSError as e:
                log.write(globals.mount_log, _('Error loading history.\nOS error(%s): %s') % (e.errno, e.strerror))
            except Exception as e:
                log.write(globals.mount_log, _('Error loading history.\nUnexpected error: %s') % (e))

    def create_settings_directory(self):

        #Create settings directory if not present
        if not os.path.exists(globals.settings_directory):
            try:
                os.mkdir(globals.settings_directory)
            except OSError as e:
                messagebox.show(self.interface.get_object('main_window'), _('Error creating settings directory.\nOS error(%s): %s') % (e.errno, e.strerror), Gtk.MessageType.ERROR)
            except Exception as e:
                messagebox.show(self.interface.get_object('main_window'), _('Error creating settings directory.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def create_settings_file(self):

        #Create the setting file if it doesn't exist
        if not os.path.exists(globals.settings_file):
            try:
                mount_point_setting = '[mount_options]\nmount_point: %s' % globals.home_directory
                with open(globals.settings_file, 'w') as settings_object:
                    settings_object.write(mount_point_setting)
                log.write(globals.mount_log, _('New settings file created at %s') % globals.settings_file)
            except OSError as e:
                messagebox.show(self.interface.get_object('main_window'), _('Error creating settings file.\nOS error(%s): %s') % (e.errno, e.strerror), Gtk.MessageType.ERROR)
            except Exception as e:
                messagebox.show(self.interface.get_object('main_window'), _('Error creating settings file.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def register_small_font_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b'.small-font { font-size: 8px; }')
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def add_small_font_class(self, widget):
        widget.get_style_context().add_class('small-font')

    def set_icons_and_text(self):

        #Set the Icons and Text
        self.interface.get_object('main_window').set_title('%s %s' % (globals.assembly_title, globals.assembly_version))
        #Allowbutton imagestobe shown
        gtk_settings = self.interface.get_object('main_window').get_settings()
        gtk_settings.set_property("gtk-button-images", True)
        self.browse_button_image = Gtk.Image.new_from_icon_name('document-open', Gtk.IconSize.MENU)
        self.interface.get_object('button_browse').set_image(self.browse_button_image)
        self.interface.get_object('button_browse').set_label(_('_Browse...'))
        self.button_mount_image = Gtk.Image.new_from_icon_name('drive-harddisk', Gtk.IconSize.MENU)
        self.interface.get_object('button_mount').set_image(self.button_mount_image)
        self.interface.get_object('button_mount').set_label(_('_Mount'))
        self.button_checksum_image = Gtk.Image()
        self.button_checksum_image.set_from_file(globals.image_checksum_button)
        self.interface.get_object('button_checksum').set_image(self.button_checksum_image)
        self.interface.get_object('button_checksum').set_label(_('_Checksum'))
        self.button_burn_image = Gtk.Image()
        self.button_burn_image.set_from_file(globals.image_burn_button)
        self.interface.get_object('button_burn').set_image(self.button_burn_image)
        self.interface.get_object('button_burn').set_label(_('Bur_n'))
        self.button_unmount_image = Gtk.Image.new_from_icon_name('process-stop', Gtk.IconSize.MENU)
        self.interface.get_object('button_unmount').set_image(self.button_unmount_image)
        self.interface.get_object('button_unmount').set_label(_('_Unmount'))
        self.button_about_image = Gtk.Image.new_from_icon_name('help-about', Gtk.IconSize.MENU)
        self.interface.get_object('button_about').set_image(self.button_about_image)
        self.interface.get_object('button_about').set_label(_('_About'))
        self.interface.get_object('button_view_log').set_label(_('View Log'))
        self.interface.get_object('button_delete_log').set_label(_('Delete Log'))
        self.interface.get_object('label_select_image').set_label(_('Select Image'))
        self.interface.get_object('label_selected_image').set_label(_('No Image Selected'))
        self.add_small_font_class(self.interface.get_object('label_selected_image'))
        self.interface.get_object('progressbar_hash').set_text(_('No Checksum Generated'))
        self.add_small_font_class(self.interface.get_object('progressbar_hash'))
        self.interface.get_object('label_selected_mount_point').set_label(_('No Mount Point Selected'))
        self.add_small_font_class(self.interface.get_object('label_selected_mount_point'))
        self.interface.get_object('frame_mounted_images').set_label(_('Mounted Images:'))
        self.interface.get_object('label_drag_prompt').set_label(_('Drag image files into above window to quickly mount'))
        self.add_small_font_class(self.interface.get_object('label_drag_prompt'))

    def set_mounted_image_treeview(self):

        #Set treeview for images
        self.treeview = self.interface.get_object('treeview_mounted_images')
        self.add_small_font_class(self.treeview)
        self.treeview.set_model(self.image_storage)
        #Create columns
        self.column_mount_point = Gtk.TreeViewColumn(_('Mount Point'), Gtk.CellRendererText(), text=0)
        self.column_image_file = Gtk.TreeViewColumn(_('Image File'), Gtk.CellRendererText(), text=1)
        self.column_fuse = Gtk.TreeViewColumn('Fuse', Gtk.CellRendererText(), text=2)
        #Add sorting
        self.column_mount_point.set_sort_column_id(0)
        self.column_image_file.set_sort_column_id(1)
        #Append columns
        self.treeview.append_column(self.column_mount_point)
        self.treeview.append_column(self.column_image_file)
        self.treeview.append_column(self.column_fuse)
        #Set Drag n Drop
        self.treeview.drag_dest_set(Gtk.DestDefaults.ALL, self.drop_targets, Gdk.DragAction.DEFAULT | Gdk.DragAction.COPY)

    def set_history_entry(self):
        #set entry for history
        self.interface.get_object('comboentry_image').set_model(self.history_storage)
        self.interface.get_object('comboentry_image').set_entry_text_column(0)

    def set_storage_lists(self):
        #Set storage
        self.image_storage = Gtk.ListStore(str, str, str) #Mounted image storage
        self.history_storage = Gtk.ListStore(str)

    def comboentry_image_key_release(self, data, event):
        key = Gdk.keyval_name(event.keyval)
        if key == 'Return':
            self.verify_image()

    def comboentry_image_changed(self, data):
        if self.interface.get_object('comboentry_image').get_active() != -1:
            self.verify_image()

    def button_browse_clicked(self, data):
        self.select_and_verify_image()

    def button_checksum_clicked(self, data):
        if self.interface.get_object('button_checksum').get_label() == _('_Checksum'):
            self.start_checksum()
        else: # Cancel
            self.checksum_abort = True
            log.write(globals.mount_log, _('Checksum generation aborted!'))

    def start_checksum(self):
        # Compute the checksum on an independent thread, polling it from the GTK main loop
        # via GLib.timeout_add rather than blocking this signal handler.
        self.checksum_abort = False
        self.checksum_image = self.interface.get_object('label_selected_image').get_label()
        self.interface.get_object('button_checksum').set_label(_('_Cancel'))
        log.write(globals.mount_log, _('Checksum generation started...'))
        self.checksum = filehash.checksum()
        if self.interface.get_object('radiobutton_md5').get_active():
            target = self.checksum.computemd5
        else:
            target = self.checksum.computesha1
        threading.Thread(target=target, args=(self.checksum_image,), daemon=True).start()
        GLib.timeout_add(100, self.poll_checksum)

    def poll_checksum(self):
        progressbar = self.interface.get_object('progressbar_hash')
        if self.checksum_abort:
            progressbar.set_text(_('No Checksum Generated'))
            progressbar.set_fraction(0)
            self.interface.get_object('button_checksum').set_label(_('_Checksum'))
            return False
        progressbar.set_fraction(self.checksum.progress)
        progressbar.set_text(self.checksum.hash)
        if not self.checksum.done:
            return True # keep polling
        log.write(globals.mount_log, _('%s:%s') % (self.checksum_image, self.checksum.hash))
        self.interface.get_object('button_checksum').set_label(_('_Checksum'))
        return False

    def select_and_verify_image(self):
        if self.select_image():
            self.verify_image()

    def select_image(self):
        is_file_selected = False
        dialog = Gtk.FileChooserDialog(_('Open Image..'),
                       None,
                       Gtk.FileChooserAction.OPEN,
                       (_('_Cancel'), Gtk.ResponseType.CANCEL,
                        _('_Open'), Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.interface.get_object('comboentry_image').get_child().set_text(dialog.get_filename())
            is_file_selected = True
        dialog.destroy()
        return is_file_selected

    def verify_image(self, image=''):
        if image == '':
            selected_file = self.interface.get_object('comboentry_image').get_child().get_text()
        else:
            selected_file = image
        # First, ensure that the file exists
        if not os.path.exists(selected_file):
            messagebox.show(self.interface.get_object('main_window'), _('File not found. \nPlease check source exists.'), Gtk.MessageType.ERROR)
            self.interface.get_object('label_selected_image').set_label(_('No Image Selected'))
            self.interface.get_object('button_mount').set_sensitive(False)
            self.interface.get_object('button_checksum').set_sensitive(False)
            self.interface.get_object('button_burn').set_sensitive(False)
            return False
        # Next, ensure it's a supported image
        if selected_file.lower().endswith(globals.SUPPORTED_EXTENSIONS):
            self.interface.get_object('label_selected_image').set_label(selected_file)
            self.interface.get_object('button_mount').set_sensitive(True)
            self.interface.get_object('button_checksum').set_sensitive(True)
            self.interface.get_object('button_burn').set_sensitive(True)
            # Loop method only supports ISO and IMG, so...
            if selected_file.lower().endswith(globals.LOOP_SUPPORTED_EXTENSIONS):
                self.interface.get_object('radiobutton_loop').set_sensitive(True)
            else:
                self.interface.get_object('radiobutton_loop').set_sensitive(False)
                self.interface.get_object('radiobutton_fuse').set_active(True)
            return True
        messagebox.show(self.interface.get_object('main_window'), _('File does not appear to be a compatible Image. \nPlease check source.'), Gtk.MessageType.ERROR)
        self.interface.get_object('label_selected_image').set_label(_('No Image Selected'))
        self.interface.get_object('button_mount').set_sensitive(False)
        self.interface.get_object('button_checksum').set_sensitive(False)
        self.interface.get_object('button_burn').set_sensitive(False)
        return False

    def button_view_log_clicked(self, data):
        if os.path.exists(globals.mount_log):
            subprocess.Popen(['gnome-text-editor', globals.mount_log])
        else:
            messagebox.show(self.interface.get_object('main_window'), _('%s not found.') % (globals.mount_log))

    def button_delete_log_clicked(self, data):
        if os.path.exists(globals.mount_log):
            if messagebox.show(self.interface.get_object('main_window'), _('Are you sure you wish to delete the log?'), Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO) == Gtk.ResponseType.YES:
                try:
                    os.remove(globals.mount_log)
                except OSError as e:
                    log.write(globals.mount_log, _('Error deleting log.\nOS error(%s): %s') % (e.errno, e.strerror))
                except Exception as e:
                    log.write(globals.mount_log, _('Error deleting log.\nUnexpected error: %s') % (e))

    def button_mount_clicked(self, data):
        try:
            self.mount_image(self.interface.get_object('label_selected_image').get_label())
        except OSError as e:
            messagebox.show(self.interface.get_object('main_window'), _('Error mounting image.\nOS error(%s): %s') % (e.errno, e.strerror), Gtk.MessageType.ERROR)
        except Exception as e:
            messagebox.show(self.interface.get_object('main_window'), _('Error mounting image.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def treeview_mounted_images_cursor_changed(self, data):
        #First get the tree view selection
        self.mounted_image_selection = self.treeview.get_selection()
        #Get the TreeModel and TreeIter of our selection
        (self.model, self.iter) = self.mounted_image_selection.get_selected()
        self.interface.get_object('label_selected_mount_point').set_label(self.model.get_value(self.iter, 0))
        self.is_mounted_image_fuse = self.model.get_value(self.iter, 2)
        #Allow user to unmount
        self.interface.get_object('button_unmount').set_sensitive(True)

    def button_unmount_clicked(self, data):
        try:
            imageaction.unmount(self.interface.get_object('label_selected_mount_point').get_label(), self.is_mounted_image_fuse)
            self.image_storage.remove(self.iter)
            self.interface.get_object('label_selected_mount_point').set_label(_('No Mount Point Selected'))
            self.interface.get_object('button_unmount').set_sensitive(False)
        except Exception as e:
            messagebox.show(self.interface.get_object('main_window'), _('Error unmounting image.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def button_burn_clicked(self, data):
        try:
            imageaction.burn(self.interface.get_object('label_selected_image').get_label())
        except Exception as e:
            messagebox.show(self.interface.get_object('main_window'), _('Error burning image.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def button_about_clicked(self, data):
        aboutbox.show(self.interface.get_object('main_window'))

    def treeview_mounted_images_drag_data_recieved(self, widget, context, x, y, sel, ttype, time):
        files = sel.get_text().split('\n')
        for file in files:
            if not file:
                continue

            file = file.strip()
            file = file.replace('%20', ' ')
            if file.startswith('file:///') and os.path.isfile(file[7:]):
                if self.verify_image(file[7:]):
                    try:
                        self.mount_image(self.interface.get_object('label_selected_image').get_label())
                    except OSError as e:
                        messagebox.show(self.interface.get_object('main_window'), _('Error mounting image.\nOS error(%s): %s') % (e.errno, e.strerror), Gtk.MessageType.ERROR)
                    except Exception as e:
                        messagebox.show(self.interface.get_object('main_window'), _('Error mounting image.\nUnexpected error: %s') % (e), Gtk.MessageType.ERROR)

    def treeview_mounted_images_row_activated(self, path, view_column, user_param1):
        imageaction.browse(self.interface.get_object('label_selected_mount_point').get_label())

    def destroy(self, data):
        self.image_storage.foreach(self.clean_up)
        log.write(globals.mount_log, _('Application closed!'))
        Gtk.main_quit()

    def clean_up(self, model, path, iter):
        if messagebox.show(self.interface.get_object('main_window'), _('%s is still mounted.\nDo you wish to unmount it before exiting?') % (model.get_value(iter, 1)), Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO) == Gtk.ResponseType.YES:
            try:
                imageaction.unmount(model.get_value(iter, 0), model.get_value(iter, 2))
            except Exception as e:
                log.write(globals.mount_log, _('Error unmounting image.\nUnexpected error: %s') % (e))
        else: #write the history to file for loading later
            try:
                string = '%s,%s,%s' % (model.get_value(iter, 0), model.get_value(iter, 1), model.get_value(iter, 2))
                with open(globals.mount_list, 'a') as mount_file:
                    mount_file.write('%s\n' % (string))
            except OSError as e:
                log.write(globals.mount_log, _('Error saving unmounted images to file.\nOS error(%s): %s') % (e.errno, e.strerror))
            except Exception as e:
                log.write(globals.mount_log, _('Error saving unmounted images to file\nUnexpected error: %s') % (e))
        return False

if __name__ == '__main__':
    parameter = ''
    if len(sys.argv) > 1:
        parameter = sys.argv[1]
    app = main_window(parameter)
    Gtk.main()
