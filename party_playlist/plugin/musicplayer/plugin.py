import subprocess
import queue
import _thread as thread
import queue
import time
import os
from collections import deque

from timstools import silence

class Player():
    def __init__(self, app, cfg, *args, **kwargs):
        self.app = app
        self.cfg = cfg
        self.track_queue = queue.Queue()
        thread.start_new_thread(self.read_queue,())
        self.nexted = deque()
        self.preved = deque()
        self.next_prev_queue = queue.Queue()
        self.completed_track_lock = thread.allocate_lock()

        if self.cfg['playing']['interface'] == 'http':
            self.communicate = self.http_interface
            self.play = self.http_play
            self.pause = self.http_pause
            self.next = self._next(self.http_next)
            self.prev = self.http_prev
            self.add = self.http_add
            self.clear = self.http_clear

    def _next(self, func):
        '''allows us to follow when the user chagned track'''
        # self.nexted.append()
        func()

    def _prev(self, func):
        '''allows us to follow when the user chagned track'''
        func()

    def communicate(self, command):
        '''call this to send commands to the player such as play, stop pause next etc'''
        raise AttributError('This needs to be overwritten in a subclass')

    def http_interface(self, command):
        port = self.cfg['playing']['port']
        if os.name == 'nt':
            cmd = 'echo \"{0}\" | ncat localhost {1}'.format(command, port)
        else:
            cmd = 'echo \"{0}\" | nc localhost {1}'.format(command, port)
        process = subprocess.Popen(cmd, shell=1, stdout=subprocess.PIPE)

        feedback = process.communicate()[0]
        return feedback

    def run(self, cmd):
        self.process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        self.pid = self.process.pid
        self.app.shutdown_cleanup['shutdown_music_player'] = self.shutdown_player

    def cleanup_player(self):
        # have no idea why this doesnt work so have to do another way... as well
        self.process.kill()

    def add_track(self, track):
        '''add tracks to queue to be played'''
        self.track_queue.put(track)

    def read_queue(self):
        while 1:
            try:
                track = self.track_queue.get(block=False)
            except queue.Empty:
                pass
            else:
                self.add(track)
                #~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
            time.sleep(1)
