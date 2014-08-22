#!/usr/bin/env python

# proxy.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from kano.utils import run_cmd, get_all_home_folders, delete_file, \
    write_file_contents, read_file_contents_as_lines

chromium_cfg = '/etc/chromium/default'
apt_cfg = '/etc/apt/apt.conf.d/80proxy'


def set_all_proxies(enable, host=None, port=None, username=None, password=None):
    pass


def get_all_proxies():
    return get_apt_proxy()


def set_chromium(enable, host=None, port=None):
    if enable:
        proxy_type = 'http'

        strflags = '"--password-store=detect --proxy-server="%s:\/\/%s:%s""' % (proxy_type, host, port)
    else:
        strflags = '"--password-store=detect"'

    cmd = "/bin/sed -i 's/CHROMIUM_FLAGS=.*/CHROMIUM_FLAGS=%s/g' %s" % (strflags, chromium_cfg)
    run_cmd(cmd)
    return


def set_curl(enable, host=None, port=None, username=None, password=None):
    if username and password:
        data = 'proxy=http://{username}:{password}@{host}:{port}'.format(
            username=username, password=password, host=host, port=port)
    else:
        data = 'proxy=http://{host}:{port}'.format(
            host=host, port=port)

    files = [os.path.join(f, '.curlrc') for f in get_all_home_folders(root=True, skel=True)]
    for f in files:
        if not enable:
            delete_file(f)
        else:
            write_file_contents(f, data)


def set_wget(enable, host=None, port=None, username=None, password=None):
    data = (
        'http_proxy=http://{host}:{port}/\n'
        'https_proxy=http://{host}:{port}/\n'
    ).format(host=host, port=port)

    if username and password:
        data += 'proxy_user={username}\n'.format(username=username)
        data += 'proxy_password={password}\n'.format(password=password)

    write_file_contents('/etc/wgetrc', data)


def get_apt_proxy():
    is_proxy = False
    settings = {
        'username': None,
        'password': None,
        'host': None,
        'port': None
    }

    cfg = read_file_contents_as_lines(apt_cfg)

    if not cfg:
        return settings

    for line in cfg:
        if line.startswith('Acquire::'):
            url = line.split('//')[-1].replace('/";', '')

            if '@' in url:
                credentials, socket = url.split('@')
                settings['username'], settings['password'] = credentials.split(':')
            else:
                socket = url

            settings['host'], settings['port'] = socket.split(':')
            is_proxy = True

    return is_proxy, settings


def set_apt_proxy(enable, host=None, port=None, username=None, password=None):
    apt_template = 'Acquire::http::proxy "http://{credentials}{host}:{port}/";'

    if enable:
        if username and password:
            credentials = '{username}:{password}@'.format(username=username,
                                                          password=password)
        else:
            credentials = ''
        cfg = apt_template.format(credentials=credentials, host=host, port=port)
    else:
        cfg = ''

    write_file_contents(apt_cfg, cfg)


