start: ./start.sh start
stop:  ./stop.sh  stop


python  bug:
python2.7.9/lib/python2.7/multiprocessing/process.py
    def join(self, timeout=None):
        '''
        Wait until child process terminates
        '''
        #print self._parent_pid, os.getpid()
        ===============change lines start===============
        if  _current_process._parent_pid is not None:
            assert self._parent_pid == os.getpid(), 'can only join a child process'

        ===============change lines end=================
        assert self._popen is not None, 'can only join a started process'
        res = self._popen.wait(timeout)
        if res is not None:
            _current_process._children.discard(self)
