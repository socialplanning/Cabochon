# Copyright (C) 2007 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

import paste.deploy

from cabochon.models import *


def setup_config(command, filename, section, vars):
    """
    Place any commands to setup cabochon here.
    """
    conf = paste.deploy.appconfig('config:' + filename)
    conf.update(dict(app_conf=conf.local_conf, global_conf=conf.global_conf))
    paste.deploy.CONFIG.push_process_config(conf)

    #you'll need these when you need to zap tables
    for table in soClasses[::-1]:
        table.dropTable(ifExists=True)
    for table in soClasses:
        table.createTable(ifNotExists=True)
