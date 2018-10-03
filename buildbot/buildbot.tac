import os
import sys

from twisted.application import service
from twisted.python import log
from buildbot.master import BuildMaster

configfile = 'master.cfg'
umask = None
basedir = os.path.abspath(os.path.dirname(__file__))
application = service.Application('buildmaster')
log.startLogging(sys.stderr)

m = BuildMaster(basedir, configfile, umask)
m.setServiceParent(application)
