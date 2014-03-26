#!/usr/bin/env python

# set_wifi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Pango
import kano_settings.components.heading as heading
import kano_settings.components.fixed_size_box as fixed_size_box
import kano_settings.proxy as proxy

win = None
next_button = None
ip_entry = None
port_entry = None
username_entry = None
password_entry = None
proxy_type = None

GRID_HEIGHT = 150

libpreload = proxy.LibPreload()
pxysettings = proxy.ProxySettings()


def is_enabled():
    return libpreload.is_enabled()


def enable():
    libpreload.proxify(True)


def disable():
    libpreload.proxify(False)


def get_settings():
    return pxysettings.get_settings()


def set_settings(proxyip, proxyport, proxytype, username='', password=''):
    settings = {
        'proxy-ip': proxyip,
        'proxy-port': proxyport,
        'proxy-type': proxytype,   # on of : "socks_v4 socks_v5" or "http_v1.0"
        'username': None,
        'password': None
    }
    pxysettings.set_settings(settings)


# Validation functions


def proxy_status(widget):
    global win, next_button, ip_entry, port_entry, password_entry, username_entry

    if widget.get_active():
        ip_entry.set_sensitive(True)
        port_entry.set_sensitive(True)
        password_entry.set_sensitive(True)
        username_entry.set_sensitive(True)
        win.connect("key-release-event", proxy_enabled)
        # Run to see if it need enabling
        proxy_enabled()

    else:
        ip_entry.set_sensitive(False)
        port_entry.set_sensitive(False)
        password_entry.set_sensitive(False)
        username_entry.set_sensitive(False)
        next_button.set_sensitive(True)


# if proxy enabled: ip address, port, and type are mandatory
def proxy_enabled(widget=None, event=None):
    global win, ip_entry, password_entry, port_entry, next_button

    # Get IP address
    # Get port
    # Get type
    # If these entries are non empty, good - else, bring up alert
    ip_text = ip_entry.get_text()
    port_text = port_entry.get_text()
    password_text = password_entry.get_text()
    if ip_text == "" or port_text == "" or password_text == "":
        next_button.set_sensitive(False)
        return False

    if valid_ip_address(ip_text):
        next_button.set_sensitive(True)
        return True

    return False


# ip address needs to be a pure ipv4 format at this moment: x.y.z.q (no segment mask as in /xx)
def valid_ip_address(ip_widget, event=None):
    global win, next_button

    # Find the index of "/"
    # Split into substring from "."
    # Check there are 4 (?).
    # Return/show tick if good, else alert/show cross image saying the ip address is wrong
    ip_array = ip_widget.split(".")
    slash_array = ip_widget.split("/")
    if len(slash_array) == 1 and len(ip_array) == 4:
        next_button.set_sensitive(True)
        return True

    else:
        next_button.set_sensitive(False)
        return False


def is_not_empty(widget, event=None):
    global win

    if widget.get_text() != "":
        return True

    False


def proxy_type(radio_button):
    global proxy_type

    if radio_button.get_active():
        proxy_type = "socks_v4 socks_v5"
    else:
        proxy_type = "http_v1.0"


def activate(_win, box, _update):
    global win, next_button, ip_entry, port_entry, username_entry, password_entry

    win = _win
    title = heading.Heading("Proxy", "Blah blah blah")
    settings = fixed_size_box.Fixed()
    grid = Gtk.Grid(column_homogeneous=False, column_spacing=10, row_spacing=10)
    win.state = 6

    win.top_bar.next_button.set_sensitive(False)
    win.top_bar.next_button.set_image(win.top_bar.pale_next_arrow)

    # Set default/intro text to grey?
    ip_entry = Gtk.Entry()
    ip_entry.props.placeholder_text = "IP address"
    ip_entry.modify_font(Pango.FontDescription("Bariol 13"))

    username_entry = Gtk.Entry()
    username_entry.props.placeholder_text = "Username"
    username_entry.modify_font(Pango.FontDescription("Bariol 13"))

    port_entry = Gtk.Entry()
    port_entry.props.placeholder_text = "Port"
    port_entry.modify_font(Pango.FontDescription("Bariol 13"))

    password_entry = Gtk.Entry()
    password_entry.props.placeholder_text = "Password"
    password_entry.set_visibility(False)
    password_entry.modify_font(Pango.FontDescription("Bariol 13"))

    enable_proxy = Gtk.CheckButton("enable proxy")
    enable_proxy.modify_font(Pango.FontDescription("Bariol 13"))
    enable_proxy.connect("clicked", proxy_status)
    enable_proxy.set_can_focus(False)

    radio1 = Gtk.RadioButton.new_with_label_from_widget(None, "socks_v4 socks_v5")
    radio1.modify_font(Pango.FontDescription("Bariol 13"))
    radio1.set_can_focus(False)

    radio2 = Gtk.RadioButton.new_with_label_from_widget(radio1, "http_v1.0")
    radio2.modify_font(Pango.FontDescription("Bariol 13"))
    radio2.set_can_focus(False)

    radio1.connect("toggled", proxy_type)
    # Needs to be run once at start
    proxy_type(radio1)

    next_button = Gtk.EventBox()
    next_button.set_size_request(150, 44)
    next_label = Gtk.Label("BACK TO WIFI")
    next_button.add(next_label)
    next_button.get_style_context().add_class("apply_changes_button")
    next_button.connect("button_press_event", back_to_wifi)

    apply_changes_alignment = Gtk.Alignment(xalign=0, yalign=0, xscale=0, yscale=0)
    apply_changes_alignment.add(next_button)

    bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    bottom_row.pack_start(enable_proxy, False, False, 0)
    bottom_row.pack_start(apply_changes_alignment, False, False, 0)
    apply_changes_alignment.set_padding(2, 2, 60, 2)

    grid.attach(ip_entry, 0, 0, 2, 2)
    grid.attach(username_entry, 0, 2, 2, 2)
    grid.attach(port_entry, 2, 0, 2, 2)
    grid.attach(password_entry, 2, 2, 3, 2)
    grid.attach(radio1, 4, 0, 1, 1)
    grid.attach(radio2, 4, 1, 1, 1)

    grid_alignment = Gtk.Alignment(xalign=0, yalign=0, xscale=0, yscale=0)
    grid_alignment.add(grid)
    padding_above = (settings.height - GRID_HEIGHT) / 2
    grid_alignment.set_padding(padding_above, 0, 0, 0)
    settings.box.pack_start(grid_alignment, False, False, 0)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(settings.box, False, False, 0)
    box.pack_end(bottom_row, False, False, 0)

    proxy_status(enable_proxy)


def apply_changes(button):
    proxyip = ip_entry.get_text()
    proxyport = port_entry.get_text()
    set_settings(proxyip, proxyport, proxy_type)
    back_to_wifi(button)
    return


def back_to_wifi(button, arg2=None):
    global win

    win.disconnect("key-release-event", proxy_enabled)
    return
