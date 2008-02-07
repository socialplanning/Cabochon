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

from paste.deploy import appconfig

from cabochon.config.environment import load_environment
from cabochon.models import *
from datetime import datetime

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup cabochon here.
    """
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    #you'll need these when you need to zap tables
#    for table in soClasses[::-1]:
#        table.dropTable(ifExists=True)
    for table in soClasses:
        table.createTable(ifNotExists=True)

    #migration: last_sent.
    try:
        conn = PendingEvent._connection
        sqlmeta = PendingEvent.sqlmeta
        last_sent = DateTimeCol("last_sent", default=datetime.now).withClass(PendingEvent)
        failures = IntCol("failures", default=0).withClass(PendingEvent)
        
        conn.addColumn(sqlmeta.table, last_sent)
        conn.addColumn(sqlmeta.table, failures)

        #set values for existing instances
        for event in PendingEvent.select():
            event.last_sent = datetime.now()
            event.failures = 0
            
    except dberrors.OperationalError:
        #already migrated
        pass

    #there is always a universal event
    if not EventType.selectBy(name="*").count():
        EventType(name="*")
