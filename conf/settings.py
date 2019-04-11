# coding=utf-8
PROJECT = 'compare-proxy'
DEBUG = False
HTTP_SERVER_SETTING = {
    'process_num': 10,
    'port': 18888
}

ZOOKEEPER_SETTING = {
    'enable': True,
    # zk的地址，多个逗号分隔
    'server_address': '10.10.10.101:2181,10.10.10.102:2181,10.10.10.103:2181,10.10.10.104:2181,10.10.10.105:2181,10.10.10.108:2181,10.10.10.109:2181',
    # 本机要注册到zk上的ip
    'local_ip': '10.10.10.109',
    'local_name': 'compare-proxy',
    'base_dir': '/hbds',
    'default_nodes': {},
    'reconnect_interval': 10
}

PROXY_SETTING = [
    # 获取系统状态
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=SystemInfo"
        ],
        "proxy_type": "all",
        "request_timeout": "2",
        "response_handler": "StatusProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    },
    # 添加元素，AB比对
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=AddElement&LibraryType=[34]",
            "/V1/ComparisonServer\\?LibraryType=[34]&CmdType=AddElement",
            "/V1/ComparisonServer\\?CmdType=CompareAB"
        ],
        "proxy_type": "loop",
        "request_timeout": "3",
        "response_handler": "LoopProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    },
    # 比对
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=Compare&SyncType=1&LibraryType=[34]"
        ],
        "proxy_type": "all",
        "request_timeout": "120",
        "response_handler": "CompareProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    },
    # 按日期删除
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=DeleteDataByTime&LibraryType=[34]"
        ],
        "proxy_type": "all",
        "request_timeout": "10",
        "response_handler": "AllProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    },
    # 人脸相关配置（libraryType=1,2）
    # 人脸这里单独配置主要考虑到显卡问题，比对有时依赖显卡，机器ip和其他会有差异
    # 人脸人像库相关（增删库）
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=CreateLibrary&LibraryType=[12]",
            "/V1/ComparisonServer\\?CmdType=DeleteLibrary&LibraryType=[12]",
        ],
        "proxy_type": "all",
        "request_timeout": "5",
        "response_handler": "AllProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    },
    # 人脸人像库相关（增删元素）
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=AddElement&LibraryType=[12]",
            "/V1/ComparisonServer\\?LibraryType=[12]&CmdType=AddElement",
            "/V1/ComparisonServer\\?CmdType=DeleteElement&LibraryType=[12]",
            "/V1/ComparisonServer\\?LibraryType=[12]&CmdType=DeleteElement",
        ],
        "proxy_type": "loop",
        "request_timeout": "3",
        "response_handler": "LoopProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    },
    # 人像库人脸比对
    {
        "url_pattern": [
            "/V1/ComparisonServer\\?CmdType=Compare&SyncType=1&LibraryType=[12]"
        ],
        "proxy_type": "all",
        "request_timeout": "120",
        "response_handler": "CompareProxyResponseHandler",
        "server_list": [{"priority": "10", "ip": "10.10.10.105", "port": "17890"}, {"priority": "10", "ip": "10.10.10.109", "port": "17890"}]
    }
]

FAKEREQUEST = False
