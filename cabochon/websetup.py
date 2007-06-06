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
    #for table in soClasses[::-1]:
    #    table.dropTable(ifExists=True)
    for table in soClasses:
        table.createTable(ifNotExists=True)
