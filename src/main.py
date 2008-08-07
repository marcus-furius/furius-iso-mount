#!/usr/bin/env python
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

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import pango
    import gtk
    import gtk.glade
except:
    sys.exit(1)

import globals
import filehash
import time
import thread
import messagebox
import os
from gettext import gettext as _

class main_window:
    def __init__(self):
        #Set the Glade file
        self.wTree = gtk.glade.XML(globals.application_interface, 'main_window')
        #Set storage
        self.image_storage = gtk.ListStore(str, str, str) #Mounted image storage
        self.history_storage = gtk.ListStore(str)
        #set entry for history
        self.wTree.get_widget("comboentry_image").set_model(self.history_storage)
        self.wTree.get_widget("comboentry_image").set_text_column(0)
        #Set treeview for images
        self.treeview = self.wTree.get_widget("treeview_mounted_images")
        self.treeview.modify_font(pango.FontDescription("sans 8"))
        self.treeview.set_model(self.image_storage)
        #Create columns
        self.column_mount_point = gtk.TreeViewColumn(_("Mount Point"), gtk.CellRendererText(), text=0)
        self.column_image_file = gtk.TreeViewColumn(_("Image File"), gtk.CellRendererText(), text=1)
        self.column_fuse = gtk.TreeViewColumn("Fuse", gtk.CellRendererText(), text=2)
        #Add sorting
        self.column_mount_point.set_sort_column_id(0)
        self.column_image_file.set_sort_column_id(1)
        #Append columns
        self.treeview.append_column(self.column_mount_point)
        self.treeview.append_column(self.column_image_file)
        self.treeview.append_column(self.column_fuse)


        HANDLERS_AND_METHODS = {
            "button_checksum_clicked": self.button_checksum_clicked,
            "button_browse_clicked": self.button_browse_clicked,
            "destroy": self.destroy}
        self.wTree.signal_autoconnect(HANDLERS_AND_METHODS)

    def button_browse_clicked(self, data):
        self.select_and_verify_image()

    def button_checksum_clicked(self, data):
        # Compute the checksum on an independent thread
        self.abort = False
        if self.wTree.get_widget("button_checksum").get_label() == _("Checksum"):
            selected_image = self.wTree.get_widget("label_selected_image").get_label()
            self.wTree.get_widget("button_checksum").set_label(_("Cancel"))

            gtk_iteration()
            checksum = filehash.checksum()

            if self.wTree.get_widget("radiobutton_md5").get_active():
                thread.start_new_thread(checksum.computemd5, (selected_image, ))
            else:
                thread.start_new_thread(checksum.computesha1, (selected_image, ))

            while checksum.hash == _('Calculating, please wait...'):
                if self.abort:
                    self.wTree.get_widget("progressbar_hash").set_text(_("No Checksum Generated"))
                    self.wTree.get_widget("progressbar_hash").set_fraction(0)
                    break
                gtk_iteration()
                time.sleep(0.1)
                self.wTree.get_widget("progressbar_hash").set_fraction(checksum.progress)
                self.wTree.get_widget("progressbar_hash").set_text(checksum.hash)
        else: # Cancel
            self.abort = True
        self.wTree.get_widget("button_checksum").set_label(_("Checksum"))

    def select_and_verify_image(self):
        if self.select_image():
            self.verify_image()

    def select_image(self):
        is_file_selected = False
        dialog = gtk.FileChooserDialog(_("Open Image.."),
                       None,
                       gtk.FILE_CHOOSER_ACTION_OPEN,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.wTree.get_widget("comboentry_image").child.set_text(dialog.get_filename())
            is_file_selected = True
        dialog.destroy()
        return is_file_selected

    def verify_image(self):
        selected_file = self.wTree.get_widget("comboentry_image").get_active_text()
        # First, ensure that the file exists
        if not os.path.exists(selected_file):
            messagebox.show(self.wTree.get_widget("main_window"), _("File not found. \nPlease check source exists."), gtk.MESSAGE_ERROR)
            self.wTree.get_widget("label_selected_image").set_label(_("No Image Selected"))
            self.wTree.get_widget("button_mount").set_sensitive(False)
            self.wTree.get_widget("button_checksum").set_sensitive(False)
            self.wTree.get_widget("button_burn").set_sensitive(False)
            return
        # Next, ensure it's a supported image
        if selected_file.lower().endswith(".iso") | selected_file.lower().endswith(".img") | selected_file.lower().endswith(".bin") | selected_file.lower().endswith(".mdf") | selected_file.lower().endswith(".nrg"):
            self.wTree.get_widget("label_selected_image").set_label(selected_file)
            self.wTree.get_widget("button_mount").set_sensitive(True)
            self.wTree.get_widget("button_checksum").set_sensitive(True)
            self.wTree.get_widget("button_burn").set_sensitive(True)
            # Loop method only supports ISO and IMG, so...
            if selected_file.lower().endswith(".iso") | selected_file.lower().endswith(".img"):
                self.wTree.get_widget("radiobutton_loop").set_sensitive(True)
            else:
                self.wTree.get_widget("radiobutton_loop").set_sensitive(False)
                self.wTree.get_widget("radiobutton_fuse").set_active(True)
            return
        messagebox.show(self.wTree.get_widget("main_window"), _("File does not appear to be a compatible Image. \nPlease check source."), gtk.MESSAGE_ERROR)
        self.wTree.get_widget("label_selected_image").set_label(_("No Image Selected"))
        self.wTree.get_widget("button_mount").set_sensitive(False)
        self.wTree.get_widget("button_checksum").set_sensitive(False)
        self.wTree.get_widget("button_burn").set_sensitive(False)

    def destroy(self, data):
            gtk.main_quit()

def gtk_iteration():
    while gtk.events_pending():
        gtk.main_iteration(False)

if __name__ == "__main__":
    app = main_window()
    gtk.main()