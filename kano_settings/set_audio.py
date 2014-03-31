#!/usr/bin/env python

# set_audio.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_settings.config_file as config_file
import kano_settings.components.heading as heading
import kano_settings.constants as constants
import kano_settings.components.fixed_size_box as fixed_size_box
import os
import re

HDMI = False
reboot = False
file_name = "/etc/rc.local"
current_img = None
# Change this value (IMG_HEIGHT) to move the image up or down.
IMG_HEIGHT = 130


def file_replace(fname, pat, s_after):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            return -1  # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            out.write(re.sub(pat, s_after, line))
        out.close()
        os.rename(out_fname, fname)


def activate(_win, box, update):
    global current_img

    title = heading.Heading("Audio settings", "Can you hear me?")
    box.pack_start(title.container, False, False, 0)

    # Settings container
    settings = fixed_size_box.Fixed()

    box.pack_start(settings.box, False, False, 0)

    # Analog radio button
    analog_button = Gtk.RadioButton.new_with_label_from_widget(None, "Analog")
    analog_button.set_can_focus(False)

    # HDMI radio button
    hdmi_button = Gtk.RadioButton.new_from_widget(analog_button)
    hdmi_button.set_label("HDMI")
    hdmi_button.connect("toggled", on_button_toggled)
    hdmi_button.set_can_focus(False)

    # height is 106px
    current_img = Gtk.Image()
    current_img.set_from_file(constants.media + "/Graphics/Audio-jack.png")

    radio_button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    radio_button_container.pack_start(hdmi_button, False, False, 10)
    radio_button_container.pack_start(current_img, False, False, 10)
    radio_button_container.pack_start(analog_button, False, False, 10)

    valign = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
    padding_above = (settings.height - IMG_HEIGHT) / 2
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(radio_button_container)
    settings.box.pack_start(valign, False, False, 0)

    # Show the current setting by electing the appropriate radio button
    current_setting(analog_button, hdmi_button)

    # Add apply changes button under the main settings content
    box.pack_start(update.box, False, False, 0)
    update.enable()


def apply_changes(button):
    global HDMI, reboot, hdmi_img, analogue_img
    # amixer -c 0 cset numid=3 N
    # 1 analog
    # 2 hdmi

    pattern = "amixer -c 0 cset numid=3 [0-9]"
    new_line = None
    if HDMI is True:
        new_line = "amixer -c 0 cset numid=3 2"
        config = "HDMI"
    else:
        new_line = "amixer -c 0 cset numid=3 1"
        config = "Analogue"

    outcome = file_replace(file_name, pattern, new_line)
    # Don't continue if we don't manage to change the audio settings in the file.
    if outcome == -1:
        return

    config_file.replace_setting("Audio", config)
    # Tell user to reboot to see changes
    reboot = True


def current_setting(analogue_button, hdmi_button):

    f = open(file_name, 'r')
    file_string = str(f.read())
    analogue_string = "amixer -c 0 cset numid=3 1"
    hdmi_string = "amixer -c 0 cset numid=3 2"

    if file_string.find(analogue_string) != -1:
        analogue_button.set_active(True)

    elif file_string.find(hdmi_string) != -1:
        hdmi_button.set_active(True)


    # Default, first button is active


def on_button_toggled(button):
    global current_img, HDMI

    HDMI = button.get_active()

    if HDMI:
        current_img.set_from_file(constants.media + "/Graphics/Audio-HDMI.png")

    else:
        current_img.set_from_file(constants.media + "/Graphics/Audio-jack.png")
