from __future__ import absolute_import
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
current_path = os.path.realpath(__file__)
lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_path))), 'lib')
sys.path.append(lib_path)
from seemmo.tools import utils
utils.initLogging()

