#!/usr/bin/python

# Please note: This code was written for GTK 2.0 and will not be ported to
#              Gtk 3.0. Users are advised to use `ma_plan_view_feh` and the
#              `feh` image viewer instead. 

# Thanks to http://www.dzone.com/snippets/python-example-simple
# and       https://piware.de/2012/03/pygobject-3-1-92-released/

import os
import sys

# -- begin compat layer --
import gi.pygtkcompat
gi.pygtkcompat.enable()
gi.pygtkcompat.enable_gtk(version='3.0')
import glib
# -- end compat layer --
import gtk
import gtk.gdk

# TODO Code not very well-structured, too many levels of indentation.
#      Long functions, which fields are declared?
# TODO Recursive mode, allow file parameters

class MaSysMaPlanView(gtk.Window):

	def handle_scrollbar_updated_event(self, adjustment):
		"""Invoked when the scrollbar is changed. This method depends on
		the value of the self.react_on_update field. If react_on_update
		is False, this method does nothing. If it is 1, the scrollbar is
		scrolled down. If it is 2, the display status is updated. After
		the invocation this method sets react_on_update back to False
		in order to prevent further invocations until react_on_update is
		changed again."""
		if self.react_on_update == False:
			return False
		if self.react_on_update == 1:
			self.scrollbar.get_vscrollbar().set_value(
					adjustment.upper - adjustment.page_size)
		elif self.react_on_update == 2:
			self.apply_display_change()
		self.react_on_update = False
		return False

	def handle_scroll_event(self, widget, event):
		"""Invoked when the scrollbar is scrolled. While CTRL is held
		down, this is used for zooming and switching to the next file
		after having reached the top/end of a "page"."""
		if event.state.first_value_name == "GDK_CONTROL_MASK":
			delta_f = 0.1
			if event.direction == gtk.gdk.SCROLL_UP:
				return self.zoom(1 + delta_f)
			elif event.direction == gtk.gdk.SCROLL_DOWN:
				return self.zoom(1 - delta_f)
			else:
				return False
		elif event.state.first_value_name != "GDK_MOD1_MASK":
			adjustment = self.scrollbar.get_vscrollbar().\
								get_adjustment()
			if event.direction == gtk.gdk.SCROLL_UP:
				return self.scroll_image(adjustment, True)
			elif event.direction == gtk.gdk.SCROLL_DOWN:
				return self.scroll_image(adjustment, False)
			else:
				return False
		return False

	def handle_window_resize_event(self, widget, event):
		"""Should resize the image on window resize if needed. This does
		not always work as it does not do this itself but wants
		handle_scrollbar_updated_event() to handle this."""
		# TODO does not always work what about apply_display_change()
		self.react_on_update = 2
		return False

	def handle_key_event(self, widget, event):
		"""Main keyboard interaction method."""
		key = gtk.gdk.keyval_name(event.keyval)
		if key == "c": # center (only affects width)
			# TODO does not really work seamless (second invocation
			# corrects... it is realted to the auto-vanishing
			# scrollbar, etc.)
			self.apply_display_change(2)
		elif key == "dollar": # end (zoom away as needed...)
			self.apply_display_change(3)
		elif key == "0": # start (zom in until not scaled anymore)
			self.apply_display_change(1)
		elif key == "q" \
			or (key == "w" and event.state.first_value_name == \
				"GDK_CONTROL_MASK") \
			or key == "F10" \
			or (key == "F4" and event.state.first_value_name == \
				"GDK_MOD1_MASK") \
			or key == "Escape": # quit
			self.exit()
		elif key == "space" or key == "l" or key == "Right":
			self.next_file()
		elif key == "h" or key == "BackSpace" or key == "Left":
			self.next_file(increment = -1)
		elif (key == "r" and event.state.first_value_name == \
					"GDK_CONTROL_MASK") or key == "F5":
			self.reload_image()
		elif key == "r": # reload dir by doing a cd to current directory
			self.chdir(self.cd_str)
		elif key == "j" or key == "Down" or key == "Page_Down":
			return self.scroll_image(self.scrollbar.
				get_vscrollbar().get_adjustment(), False)
		elif key == "k" or key == "Up" or key == "Page_Up":
			return self.scroll_image(self.scrollbar.
					get_vscrollbar().get_adjustment(), True)
		elif key == "o" or key == "g" or key == "d":
			self.chdir_gui()
		elif key == "F11":
			self.is_fullscreen = not self.is_fullscreen
			if self.is_fullscreen:
				self.fullscreen()
			else:
				self.unfullscreen()
		elif key == "F2":
			dialog = gtk.AboutDialog()
			dialog.set_program_name("Ma_Sys.ma Plan View")
			dialog.set_comments(
					"a simple keyboard only image viewer")
			dialog.set_version("1.0.0.2")
			dialog.set_copyright(
				"Copyright (c) 2012, 2013 Ma_Sys.ma." +
				"For further info send an e-mail to " +
				"Ma_Sys.ma@web.de."
			)
			license_file = "/usr/share/common-licenses/GPL-3"
			if os.path.exists(license_file):
				link = open(license_file, 'r')
				dialog.set_license(link.read())
				link.close()
			else:
				dialog.set_license(self.get_license_small())
			dialog.run()
			dialog.destroy()
		elif key == "F1":
			dialog = gtk.MessageDialog(
				self,
				gtk.DIALOG_MODAL |
					gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_INFO, gtk.BUTTONS_OK, None
			)
			dialog.set_title("Help")
			keyboard_commands = [
				("F1", "Display this help"),
				("F2", "Version information"),
				("F5, CTRL-R", "Reload current file"),
				("r", "Reload directory"),
				("F10, ESC, q, CTRL-W, ALT-F4", "Exit"),
				("F11", "Toggle fullscreen mode"),
				("Page Down",
				"Page down (next file if end of page reached)"),
				("Page Up", "Page up (previous file " +
						"if begin of page reached)"),
				("Home", "Go to first file"),
				("End", "Go to last file"),
				("c", "<i>Center</i>, adjust image to fit " +
								"page width"),
				("$",
				"Zoom out until the whole image is visible"),
				("0", "Restore original image size"),
				("o, g, d", "<i>open</i>, <i>goto</i>, " +
					"(<i>change</i>)dir: change directory"),
				("CTRL-[SCROLL]", "Zoom"),
				("Space, l, Right", "Next file."),
				("Backspace, h, Left", "Previous file."),
				("p", "Display current filename."),
				("n", "Note filename to planview_sel.txt"),
				("e", "Toggle honor exif information."),
				("m", "Toggle maximized."),
				("b", "Toggle dark background color.")
			]
			markup = "<b>List of all keyboard commands</b>\n\n"
			for entry in keyboard_commands:
				key, descr = entry;
				markup += "<tt>" + key + "</tt>\n\t" + descr + \
									"\n"
			dialog.set_markup(markup)
			dialog.run()
			dialog.destroy()
		elif key == "Home":
			self.cd_sub = 0
			self.next_file_open()
		elif key == "End":
			self.cd_sub = len(self.cd) - 1
			self.next_file_open(increment = -1)
		elif key == "p":
			dialog = gtk.MessageDialog(
				self,
				gtk.DIALOG_MODAL |
					gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_INFO,
				gtk.BUTTONS_OK,
				"Current file: \"" +
					self.cd[self.cd_sub] + "\"."
			)
			dialog.set_title("Current file");
			dialog.run()
			dialog.destroy()
		elif key == "n":
			stream = open("planview_sel.txt", "a")
			stream.write(self.cd[self.cd_sub] + "\n")
			stream.close()
		elif key == "e":
			self.honor_exif = not self.honor_exif
			self.reload_image()
		elif key == "m":
			self.is_maximized = not self.is_maximized
			if self.is_maximized:
				self.maximize()
			else:
				self.unmaximize()
		elif key == "b":
			self.bg_default = not self.bg_default
			bg_new = None
			if self.bg_default:
				bg_new = self.bg_backup
			else:
				self.bg_backup = self.style.bg[gtk.STATE_NORMAL]
				bg_new = gtk.gdk.Color(0x40, 0x40, 0x40)
			self.viewport.modify_bg(gtk.STATE_NORMAL, bg_new)

		return False

	def scroll_image(self, adjustment, up = True):
		"""Scrolls the image completely up or down
		(up if up == True, down if up == False)."""
		if adjustment.value == adjustment.lower and up:
			self.next_file(increment = -1)
			# Scroll down after change was registered
			self.react_on_update = 1
		# Thanks to http://www.pygtk.org/pygtk2tutorial/
		# 				sec-RangeWidgetEample.html
		elif adjustment.value == (adjustment.upper -
					adjustment.page_size) and not up:
			self.next_file()
			# As this always remains 0.0 it is not problematic that
			# it is not yet updated...
			self.scrollbar.get_vscrollbar().\
						set_value(adjustment.lower)
		else:
			return False
		return True

	def zoom(self, factor):
		"""Zooms into the image. Warning: Scaling is done on the CPU
		meaning that it is not very efficient and especially not fast
		with very big, scaled images."""
		if self.display_mode != 4:
			self.apply_display_change(4)
		if (self.zoom_height < 32 or self.zoom_width < 32) \
								and factor < 1:
			return True
		self.zoom_height = int(self.zoom_height * factor)
		self.zoom_width = int(self.zoom_width * factor)
		self.apply_display_change(4)
		return True
	
	def apply_display_change(self, change_display_mode = False):
		"""Applies a display change by recalculating the displayed
		image."""
		if change_display_mode != False:
			self.display_mode = change_display_mode;
		self.current_pixbuf = self.current_source_pixbuf
		new_width = -1;
		new_height = -1;
		if self.display_mode == 4:
			if self.zoom_width == -1 or self.zoom_height == -1:
				self.zoom_width = \
						self.current_pixbuf.get_width()
				self.zoom_height = \
						self.current_pixbuf.get_height()
			new_width = self.zoom_width
			new_height = self.zoom_height
		else:
			self.zoom_width = -1
			self.zoom_height = -1
			if self.display_mode != 1:
				wnd_rectangle = self.viewport.get_allocation()
				wnd_width = wnd_rectangle.width
				wnd_height = wnd_rectangle.height
				img_width = self.current_source_pixbuf.\
								get_width()
				img_height = self.current_source_pixbuf.\
								get_height()
				if self.display_mode == 2 and \
							img_width > wnd_width:
					new_width = wnd_width
					new_height = (wnd_width * img_height) /\
								img_width
				elif self.display_mode == 3:
					# If you remve this statement you will
					# force the image to fill the window
					# even if it's smaller than the window
					# TODO BUG IF ONE OF THEM IS NEGATIVE
					if img_width > wnd_width or \
							img_height > wnd_height:
						if img_width - wnd_width > \
							img_height - wnd_height:
							new_width = wnd_width;
							new_height = \
								(new_width *
								img_height) / \
								img_width
						else:
							new_height = wnd_height
							new_width = \
								(new_height *
								img_width) / \
								img_height
		if new_width != -1 and new_height != -1:
			# TODO not very efficient as not done on the gpu,
			# ram comsumption extremly high with upscaled images
			self.current_pixbuf = self.current_source_pixbuf.\
				scale_simple(new_width, new_height,
							gtk.gdk.INTERP_HYPER)
		self.current_image.set_from_pixbuf(self.current_pixbuf)

	def next_file(self, zskip = False, increment = 1):
		"""Tries to open the next file (you can select the "previous"
		file via increment = -1)."""
		self.cd_sub = self.cd_sub + increment
		return self.next_file_open(zskip, increment)

	def gtk_error_dialog(self, content):
		dialog = gtk.MessageDialog(
			self,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
			gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, content
		)
		dialog.set_title("Error")
		dialog.run()
		dialog.destroy()

	def next_file_open(self, zskip = False, increment = 1):
		"""Method called to open the "next" file without incrementing
		self.cd_sub and therefore useful for reloading operations, etc.
		Non-Image files are automatically skipped. After having reached
		the end of the list, the program returns to the begin of the
		list."""
		if self.cd_sub == len(self.cd):
			if len(self.cd) == 0:
				self.gtk_error_dialog(
					"The selected directory is empty."
				)
				return False
			elif zskip:
				self.gtk_error_dialog(
					"The directory does not contain a " +
					"single useful image file."
				)
				return False
			else:
				self.cd_sub = 0
		elif self.cd_sub < 0:
			self.cd_sub = len(self.cd) - 1

		# Skip unwanted files
		if (not '.' in self.cd[self.cd_sub]) or \
			(not self.cd[self.cd_sub].rpartition('.')[2].lower()
							in self.filetypes):
			return self.next_file(self.cd_sub == 0 or zskip,
								increment)

		self.reload_image()
		return True

	def reload_image(self):
		"""Tries to reload current image from file."""
		try:
			self.current_source_pixbuf = gtk.gdk.\
				pixbuf_new_from_file(self.cd_str + os.sep +
							self.cd[self.cd_sub])
		except:
			dialog = gtk.MessageDialog(
				self,
				gtk.DIALOG_MODAL |
					gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
				"Could not load image file \"" +
					self.cd[self.cd_sub] + "\"."
			)
			dialog.run()
			dialog.destroy()
			return
		if self.honor_exif:
			self.current_source_pixbuf = \
				self.current_source_pixbuf.\
					apply_embedded_orientation()
		self.apply_display_change()
	
	def chdir_gui(self):
		"""Displays a gtk.FileChooserDialog to select another directory.
		Available via the "d" command."""
		chooser = gtk.FileChooserDialog(
			"Select new directory", self,
			gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, 
			("Cancel", 1, "Select", 0)
		)
		chooser.set_filename(self.cd_str)
		has_selected = chooser.run()
		selection = None
		if has_selected == 0:
			selection = chooser.get_filename()
		chooser.destroy()
		if selection == None:
			return False
		else:
			return self.chdir(selection)

	def chdir(self, path, first_run = False):
		"""Tries to cd into the given path. If first_run == True it does
		not store the current values of important fields like
		self.cd_str and self.cd_sub that are used to restore on failure
		if first_run == False. If there is a failure and
		first_run == True, this method exits the program with return
		code 2."""
		prev = None
		prev_pos = None
		if not first_run:
			prev = self.cd_str
			prev_pos = self.cd_sub
		if first_run or not self.cd_str == path:
			self.cd_sub = -1
		else:
			# As we call next_file() we need to go back one file
			# first.
			self.cd_sub -= 1
		self.cd_str = path
		self.cd = os.listdir(self.cd_str)
		self.cd.sort()
		# We cannot give a "zero move step" here as this can result in
		# endless loops.
		if not self.next_file():
			if first_run:
				self.exit(exit_status = 2)
			elif not self.chdir_gui():
				# Restore settings
				self.cd_str = prev
				self.cd_sub = prev_pos
				self.cd = os.listdir(prev)
				self.cd.sort()
	
	def exit(self, widget = None, exit_status = 0):
		"""Terminates the application with the given exit_status
		regardless of the widget parameter or the gtk main loop being
		run or not."""
		if gtk.main_level() == 0:
			exit(exit_status)
		else:
			gtk.main_quit()
			exit(exit_status)

	def __init__(self):
		"""Initializes GUI and fields. Tries to load the directory given
		via parameter 1 or to use the current directory if no parameter
		is given."""
		# Create window
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
		self.set_title("Ma_Sys.ma Plan View")
		#self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(20, 20, 20))

		# Display modes:
		# 1. non-scaled
		# 2. scaled to fit width
		# 3. scaled to fit height and width
		# 4. specially scaled (see zoom variables)
		self.display_mode = 1
		self.zoom_width = -1
		self.zoom_height = -1
		
		self.react_on_update = False
		self.is_fullscreen = False
		self.is_maximized = False
		self.honor_exif = False
		self.bg_default = True

		# Create image container
		self.current_image = gtk.Image()

		# Create scrollbar
		# From http://stackoverflow.com/questions/6300816/
		# 	prevent-scrollbars-from-showing-up-when-placing-a-
		# 	drawing-area-inside-a-scrolled
		self.scrollbar = gtk.ScrolledWindow()
		self.scrollbar.set_policy(gtk.POLICY_AUTOMATIC,
							gtk.POLICY_AUTOMATIC)
		self.scrollbar.set_shadow_type(gtk.SHADOW_NONE)
		self.scrollbar.connect("scroll_event", self.handle_scroll_event)
		self.scrollbar.get_vscrollbar().get_adjustment().connect(
				"changed", self.handle_scrollbar_updated_event)
		# Create image drawing facility (viewport)
		self.viewport = gtk.Viewport()
		self.viewport.set_shadow_type(gtk.SHADOW_NONE)
		self.viewport.add(self.current_image)
		# Merge viewport and scrollbar
		self.scrollbar.add(self.viewport)
		self.add(self.scrollbar)

		# Connect events
		self.connect("destroy", self.exit)
		self.connect("key_press_event", self.handle_key_event)
		self.set_events(gtk.gdk.KEY_PRESS_MASK)
		self.connect("configure_event", self.handle_window_resize_event)

		# Set supported filetypes (tga and png are the most important)
		self.filetypes = [
			"tga", "gif", "jpg", "jpeg", "png", "bmp", "tiff", "ico"
		]
		# TODO allow runtime interpolation type change... ('z')

		# Determine startup directory and load image
		if len(sys.argv) == 2:
#			if sys.argv[1] == "-f":
#				# TODO ALLOW FILE PARAMETERS
#			elif sys.argv[1] == "-r":
#				self.chdir(sys.argv[1], True, recursive=True)
#			else:
			self.chdir(sys.argv[1], True)
		else:
			self.chdir(".", True)

		# Display window
		self.resize(1050, 900)
		self.set_gravity(gtk.gdk.GRAVITY_CENTER)
		self.show_all()
		gtk.main()

	def get_license_small(self):
		"""Returns a short notice that is used if the GPL Text file is
		not available. This is required on e.g. Windows Systems that
		certainly do not have an /usr directory."""
		return
"""    Ma_Sys.ma Plan View, a simple keyboard only image viewer
    Copyright (C) 2012, 2013, 2020  Ma_Sys.ma

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>."""

if __name__ == "__main__":
	MaSysMaPlanView()
