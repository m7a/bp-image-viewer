---
section: 32
x-masysma-name: image_viewer
title: Image Viewer Scripts
date: 2020/12/18 22:59:34
lang: en-US
author: ["Linux-Fan, Ma_Sys.ma (Ma_Sys.ma@web.de)"]
keywords: ["mdvl", "shell", "script", "linux", "python", "images", "plan_view"]
x-masysma-version: 1.0.0
x-masysma-website: https://masysma.lima-city.de/32/image_viewer.xhtml
x-masysma-repository: https://www.github.com/m7a/bp-image-viewer
x-masysma-owned: 1
x-masysma-copyright: |
  Copyright (c) 2020 Ma_Sys.ma.
  For further info send an e-mail to Ma_Sys.ma@web.de.
---
Introduction
============

This repository provides Ma_Sys.ma _Image Viewer_ scripts. These are intended to
supplement more heavyweight applications like
[eog(1)](https://manpages.debian.org/buster/eog/eog.1.en.html) by quick but
feature-reduced scripts.

The idea behind these scripts stems from having many scanned-in pages and
the need for some specific functions combined with keyboard-driven usage.
As a result, the first script `plan_view.py` is controlled entirely by keyboard
and provides predefined zoom-levels (1:1, fit to window and fit to width) useful
for viewing scanned pages.

As `plan_view.py` was found to be slightly incomplete and also slow especially
wrt. zooming, an attempt to reconstruct most of the functionality using an
existing image viewer `feh` was made. This is implemented in script
`ma_plan_view_feh` which is the default “image viewer” on MDVL systems
(cf. `vifmrc` from [conf-cli(32)](conf_cli.xhtml)).

Ma_Sys.ma Plan View `plan_view.py`
==================================

`plan_view.py` is invoked taking as argument a single directory which is scanned
for image files in a non-recursive manner. Afterwards, the first in list is
displayed. Plan View can then be controlled by the following keybindings
(copied from the help screen):

Keys                         Action
---------------------------  ------------------------------------------------
F1                           Display this help
F2                           Version information
F5, CTRL-R                   Reload current file
r                            Reload directory
F10, ESC, q, CTRL-W, ALT-F4  Exit
F11                          Toggle fullscreen mode
Page Down                    Page down (next file if end of page reached)
Page Up                      Page up (previous file if begin of page reached)
Home                         Go to first file
End                          Go to last file
c                            _Center_, adjust image to fit page width
$                            Zoom out until the whole image is visible
0                            Restore original image size
o, g, d                      _open_, _goto_, _change_ dir: change directory
CTRL-[SCROLL]                Zoom
Space, l, Right              Next file.
Backspace, h, Left           Previous file.
p                            Display current filename.
n                            Note filename to `planview_sel.txt`
e                            Toggle honor exif information.
m                            Toggle maximized.
b                            Toggle dark background color.

An older version of `plan_view.py` can also be found on
<https://pastebin.com/BbRES3Ve>.

## Notable Features

Notable features include

 * The ability to navigate image contents as if it were pages by means of
   the [Page Up] and [Page Down] keys.
 * The zoom to fit window width (key [c])
 * Shortcut [n] to save image file name to `planview_sel.txt` file.
   This feature is very useful for non-scanned images to select either favorite
   or to-be-deleted images (depending on user's choice). The contents of
   `planview_sel.txt` can be processed manually or by supplementary script
   `mvsel`.

## OS Information

`plan_view.py` has only ever been tested on Linux systems. However, given that
it is Python and GTK it may as well work on Windows, too.

## Script `mvsel`

A common task when processing image files is to decide for some of the images
to be further processed or deleted. To do this interactively, shortuct key [n]
in Plan View can be used. Afterwards, script `mvsel` can process this file as
follows:

`mvsel dir`
:   Moves all of the selected files to directory `dir`.
`mvsel -d`
:   Deletes all of the selected files.

Feh-based Image Viewing
=======================

As [feh(1)](https://manpages.debian.org/buster/feh/feh.1.en.html) is quite
versatile, it seemed that most of `plan_view.py`'s features could be implemented
by providing a suitable configuration file. The following Plan View features
do not seem to be provided out-of-the box by `feh`:

 * Ability to note file names to `planview_sel.txt`
 * Ability to change directory interactively.

`feh` can be extend  by custom “actions” which allow these features to be added
by means of a controlling shell script. As a result, script
`ma_plan_view_feh` was created. It invokes `feh` and maps two actions to
the specific functions described above.

Note, that the shell script itself does _not_ implement Plan View-like
keybindings. Instead, it relies on a separate configuration file
(from package `mdvl-conf-gui`) for configuring the keyboard shortcuts.

Also, from `plan_view.py` to `ma_plan_view_feh`, the following differences may
be observed:

 * Default mode is no longer `0`, but rather `$`.
 * Switching to different directory does not work as reliable as before.
   (It is unclear why, but sometimes the `feh` instance from the previous
   directory will not close).
 * `feh` acts recursively by default.

Reduced Features
================

While most image viewing tasks can be solved by means of the scripts provided
here, there are some special cases for which programs like `eog` are better:

 * zoom-intensive operations
 * printing image files to paper
 * animated images (e.g. `.gif` files)
