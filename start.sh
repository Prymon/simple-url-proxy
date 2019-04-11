#!/bin/bash
shopt -s  expand_aliases
shopt expand_aliases
start() {
    nohup $HOME/share/python/ubuntu/python2.7.15/bin/python seemmo_compare_proxy_server.py  2>&1 &
}

stop() {

    if [ $(ps -ef | grep seemmo_compare_proxy_server.py | grep -v grep | wc -l)  -gt 0 ] ;
    then ps -ef | grep seemmo_compare_proxy_server.py | grep -v grep | cut -c 9-15 | xargs kill;
    fi;
}

restart() {
    stop
    start
}

status(){
    ps -ef | grep seemmo_compare_proxy_server.py | grep -v grep | wc -l
}

case "$1" in
    start)
        $1
        ;;
    stop)
        $1
        ;;
    restart)
        $1
        ;;
    status)
    $1
    ;;
    *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac
