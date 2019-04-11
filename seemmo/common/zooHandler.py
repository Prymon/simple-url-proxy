# coding=utf-8
import logging
from kazoo.protocol.states import EventType
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.exceptions import ZookeeperError

from conf import settings


# 注册节点到zookeeper上
# 使用kazoo async api
class ZooHandler(object):

    def __init__(self):
        self.zookeeper_client = None
        if not settings.ZOOKEEPER_SETTING['enable']:
            logging.info('zookeeper disabled')
            return
        self.zoo_hosts = settings.ZOOKEEPER_SETTING['server_address']
        logging.info('start zookeeper client, zoo hosts: %s' % self.zoo_hosts)
        self.base_dir = settings.ZOOKEEPER_SETTING['base_dir']
        self.zookeeper_client = KazooClient(hosts=self.zoo_hosts)
        self.zookeeper_client.add_listener(self.state_listener)
        self.zookeeper_client.start_async()

    def state_listener(self, state):
        # session was lost
        if state == KazooState.LOST:
            logging.error('zookeeper lost!')
        # disconnected from Zookeeper
        elif state == KazooState.SUSPENDED:
            logging.error('zookeeper disconnected!')
        # connected/reconnected to Zookeeper
        elif state == KazooState.CONNECTED:
            self.register_node()
            logging.warn('zookeeper reconnected! try to register')
        else:
            logging.error('unexpected zookeeper state!!!')
            logging.critical('unexpected zookeeper state!!!')

    def register_node(self):
        if not self.zookeeper_client or not self.zookeeper_client.connected:
            logging.error('zoo not connected, register cancel')
            return
        path = ZooHandler.get_register_path()
        try:
            # 尝试注册节点
            def try_to_create_node(result):
                logging.info('zoo try_to_create_noe called')
                try:
                    # None表示节点不存在
                    if result.value is None:
                        self.zookeeper_client.create_async(path, makepath=True, ephemeral=True)
                    elif result.exception:
                        logging.fatal('critical error when try to check node when reconnected, %s', result.exception)
                    else:
                        logging.warn('node already exists when reconnect and try to register')
                except BaseException as e:
                    logging.exception('critical error, %s', e.message)

            # 监控节点变化
            def node_watcher(watch_event):
                logging.info('zoo node_watcher called')
                try:
                    if EventType.DELETED == watch_event.type:
                        logging.warn('zoo nodes deleted, try recreate')
                        self.zookeeper_client.create_async(path, makepath=True, ephemeral=True)
                    if EventType.CHANGED == watch_event.type:
                        logging.warn('zoo nodes changed,do nothing')
                    if EventType.CHILD == watch_event.type:
                        logging.warn('zoo nodes childed,do nothing')
                    if EventType.CREATED == watch_event.type:
                        logging.info('zoo nodes success created')
                    if EventType.NONE == watch_event.type:
                        logging.error('zoo nodes status return None')
                finally:
                    self.zookeeper_client.exists_async(path, watch=node_watcher)

            future = self.zookeeper_client.exists_async(path, watch=node_watcher)
            future.rawlink(try_to_create_node)
        except ZookeeperError as e:
            logging.exception('zookeeper exception when register node: %s' % e.message)
        except BaseException as e:
            logging.exception('critical error!')

    # 1. remove nodes,stop client
    def stop(self):
        logging.info('stopping zookeeper client')
        if self.zookeeper_client:
            self.zookeeper_client.remove_listener(self.state_listener)
            self.zookeeper_client.stop()
            logging.info('zookeeper stopped')

    @staticmethod
    def get_register_path():
        base_dir = settings.ZOOKEEPER_SETTING['base_dir']
        if base_dir[-1] == '/':
            base_dir = base_dir[0:-1]
        register_name = "%s/%s:%s:%s" % (base_dir, settings.ZOOKEEPER_SETTING['local_name'], settings.ZOOKEEPER_SETTING['local_ip'], settings.HTTP_SERVER_SETTING['port'])
        return register_name
