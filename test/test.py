import time
from multiprocessing import Process, Manager
import ujson as json
from seemmo.tools import utils
from seemmo.common.zooHandler import ZooHandler

if __name__ == '__main__':
    def cb(new_nodes):
        print 'current nodes: %s' % new_nodes


    utils.initLogging()
    print('start')
    zoo = ZooHandler()
    zoo.add_change_callback(cb)
    zoo.start()

    while True:
        time.sleep(1)
        print(zoo.get_all_nodes())
