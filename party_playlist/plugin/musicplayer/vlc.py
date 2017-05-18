import os
import _thread as thread
import subprocess
import time 
from glob import glob
import re
from multiprocessing.pool import ThreadPool
import requests
import string
import unicodedata
import logging

from .plugin import Player

class MusicPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features = ('stream', 'local', 'http', 'all_formats')
        #~ self.output_dir = output_dir
        #~ self.input_dir = input_dir

    def launch(self):
        port = self.cfg['playing']['port']
        if not port:
            port = 1250

        if os.name == 'nt':
            progfiles = os.environ['PROGRAMW6432']
            exe = os.path.join(progfiles, 'VideoLAN', 'VLC', 'vlc')
            cmd = exe + ' -I rc --rc-host localhost:' + str(port)
        else:
            cmd = 'cvlc' +  ' -I rc --rc-host localhost:' + str(port)
        self.run(cmd)
        print('spawning vlc window!')
        #~ args = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

    def http_pause(self):
        self.communicate('pause')


    def http_next(self):
        self.communicate('next')


    def http_prev(self):
        self.communicate('prev')


    def http_play(self, track=None):
        if track:
            self.communicate('add '+ track)
        else:
            self.communicate('play')


    def http_add(self, arg):
        self.communicate('enque ' + arg)


    def http_clear(self):
        self.communicate('clear')


    def bytes_played(self):
        '''lets us know how much bytes have been played from a song'''
        feedback = self.communicate('stats').decode('utf-8')
        stats = feedback.split('\n')
        for line in stats:
            if 'input bytes read' in line:
                dirty = line.split(':')[1]
                dirty = dirty.lstrip()
                bytes_read = int(dirty.split(' ')[0])
                return bytes_read
        else:
            logging.debug('Vlc player currently not playing...')

    def finished_playing_track(self):
        '''lets us know when a track is finished playing'''
        feedback = self.communicate('stats').decode('utf-8')
        stats = feedback.split('\n')
        for line in stats:
            if 'input bytes read' in line:
                dirty = line.split(':')[1]
                dirty = dirty.lstrip()
                bytes_read = int(dirty.split(' ')[0])
                break
        else:
            logging.debug('Vlc player currently not playing...')

        feedback = self.communicate('status').decode('utf-8')
        status = feedback.split('\n')
        for line in status:
            if 'new input' in line:
                stream_type = line.split(':')[1]
                dirty = line.split(':')[2]
                playing_track = dirty.split(' )\r')[0]
                try:
                    if playing_track == self.last_played:
                        return False
                    else:
                        # track has been changed
                        self.last_played = playing_track
                        return True
                except AttributeError:
                    self.last_played = playing_track
                    return False
        else:
            logging.debug('Vlc player currently not playing...')

    def shutdown_player(self):
        self.communicate('shutdown')

# def add_tracks(tracks):
#     self.dl()
#     self.convert()
#     self.queue.put(track)
# from pydub import AudioSegment
# def convert():
#     filenames = []                      # Get all files in the cwd      #http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
#     for root, dirs, files in os.walk(MUSIC_DIR):    # add to tims tools for listing files...
#         root_and_files = [os.path.join(root, file) for file in files]
#         filenames.extend(root_and_files)
#         break
#
#     for file in filenames:
#         print("Transcodeing into wav", file)
#         try:
#             pass
#             song = AudioSegment.from_mp3(file)
#         except Exception as err:
#             print(err)
#             print('Problems happend')
#             continue
#         EXPORT_NAME = file.split(os.sep)[-1]
#         #print(EXPORT_NAME)
#         song.export(EXPORT_NAME, format="wav")
#         #play(EXPORT_NAME)
#
# def dummy(self):
#     while 1:
#         print('Waiting for input!')
#         print(self.input_dir)
#         for file in glob(self.input_dir+"/*.wav"):
#             print('putting on the queue',file)
#             self.queue.put(os.path.join(self.input_dir, file))
#         time.sleep(2)
#     while 1:
#         try:
#             track = self.track_queue.get(block=False)
#         except queue.Empty:
#             pass
#         else:
#             print('playing song now!')
#             print(track)
#             #~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
#             subprocess.call(['aplay',track])
#             print('Finished playing song ..')
#         time.sleep(1)
#
if __name__ == '__main__':
    player = MusicPlayer()
    playerkkkkkkkkkkkkk
