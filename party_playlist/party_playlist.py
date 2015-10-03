#~ from __future__ import print_function
#~ from __future__ import with_statement
#http://docopt.org/
__doc__ ="""Party Playlist
Usage:
    party_playlist.py new <name> [--timeout --profile --test]
    party_playlist.py load <name> [--timeout]
    party_playlist.py play [name] [--profile]
    party_playlist.py export <name> 
    party_playlist.py cfg 
    party_playlist.py list [name]
    party_playlist.py [-t | --test]
    party_playlist.py [-h | --help]

Options:
    new <name>  Create a new playlist and start listening for new users
    load <name> Loads a previously created list, use timeout to control how long to set it active
    play [name] Play a playlist, defaults to last played
    list [name] Either list all playlists or enter the name or id of the playlist to view specifics
    -t --test   testing mode will create if doesnt exists, and just load if it does
    -h --help   Show this screen and exit
"""
from pprint import pprint
import time
import yaml
import _thread as thread
import queue
from collections import deque
import subprocess
import sys
import os

#~ import nxppy
import apptools

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:pass
from docopt import docopt

try:
    from .import func
    from . import db_utils
except SystemError:
    import func
    import db_utils

with open("config.conf", 'r') as ymlfile:
    CFG = yaml.load(ymlfile)

TRACKS_PREV = deque()
TRACKS_NEXT = deque()

LOG_FILE = 'latest.log'
apptools.setup_logger(LOG_FILE)

class Party():
    # Scanning for button Presses
    # Scanning for input via web interface or app
    
    # Different Playing modes, either via button press or online config
    # Mode 1 Default, is autonomous, uses the default settings to organize
    # a playlist and play the music,  a genre toggle, and a next button
    # Mode 2 only plays music actually found on devices, then stops. no Discovery mode
    
    # Need a way to choose music output, either hdmi, cable or plug and play
    
    # User can overide playlist by using app or web interface

    # Alot of the options for changing music player etc are saved in a cfg file which can be edited manually
    # or by the program
    
    def __init__(self, name='test', load=False, timeout=False, profile=False,test=False, play=False):
        #~ self.input_actions = {5:lambda:print(5),7:None,12:None}
        #self.check_buttons()       # Buttons change the playback mode
        self.track_queue = queue.Queue()
        self.playlist_queue = queue.Queue()
        # thread.start_new_thread(self.music_player,())

        if play:
            if name == None:
                name = 'testing'
                print('Selecting the last used playlist {0}'.format(name))
            else:
                print('Playlist selecte for playback {0}'.format())
            tracks = func.next_tracks(name, 3)
            self.playlist_queue.put(tracks)
            #~ tracks = func.next_tracks(name, 'all')
            #~ pprint(tracks)
            #~ print('adding')
        else:
            print("Party on, lets create a new/load existing playlists")
            thread.start_new_thread(self.find_tracks,())    # Check Server for wifi and for nfc connections
            # import pdb;pdb.set_trace()
            thread.start_new_thread(self.playlist_from_tracks,(name,load,timeout,profile,test))

        self.partyplaylist_input()
    
    #~ def check_buttons(self):     # Maps Input Pins to different actions
        #~ prev_input = 0   
        #~ while 1:
            #~ INPUTS = ((i , GPIO.input(i)) for i in (5,17,12)) #pins to check 
            #~ for pin, result in INPUTS:
                #~ if result and not prev_input:
                    #~ self.input_actions(pin)
                    #~ prev_input = 1
                    #~ break
            #~ prev_input = 0
            #~ time.sleep(0.05) #should help stop bouncing
    
    def find_tracks(self):
        while 1:
            time.sleep(5)
            #~ print('waiting for inputs!!! so press 1 to demo')
            #~ if input() == '1':
                #~ print('getting shit')
                #~ time.sleep(1)
                #~ print('finished getting!!!')
                #~ self.track_queue.put(1)
                    #~ import random
        #~ while 1:
            #~ pass
            #~ card = nxppy.Mifare()
            #~ try:
                #~ uid = card.select()
            #~ except nxppy.SelectError:
                #~ print('0   ', random.Random())
            #~ else:
                #~ block10bytes = mifare.read_block(10)
                #~ print('1 : ',block10bytes)

    def playlist_from_tracks(self,name,load,timeout,profile,test):
        '''Runs algo on tracks that are recieved from users'''
        func.get_us_a_playlist()
        # import pdb;pdb.set_trace()
        while 1:
            try:
                todo = self.track_queue.get(block=False)
            except queue.Empty:pass 
            else:
                func.process_tracks(name,load,timeout,profile,test) # NEED TO PASS IN DB NOT TAKE ALL IN FOLDER
                tracks = func.next_tracks(name, 2)  
                self.playlist_queue.put(tracks)
            time.sleep(1)
    
    def partyplaylist_input(self):
        '''Blocks, reads commands from stdin and provides a simple api for common actions'''
        while 1:
            print('waiting for inputs!!! so press 1 to demo')
            data = input()  
            
            if data == '1':
                pass
            if data in ('q', 'c'):
                pass
            elif data in ('n', 'next'):
                self.music_player.http_next()
            elif data == ('p', 'prev'):
                self.music_player.http_prev()
            elif data == 'play':
                self.music_player.http_play()
            elif data == 'pause':
                self.music_player.http_pause()
            elif data == 'add':pass
                #~ self.music_player.add_t
            time.sleep(1)
    
    def music_player(self):
        '''Setup logic for MusicPlayer'''
        player = CFG['playing']['music_player']
        song_source = CFG['playing']['song_source']
        if player == 'aplay':
            try:
                from .plugin.musicplayer import aplay as player
            except SystemError:
                from plugin.musicplayer import aplay as player
        elif player == 'vlc':
            try:
                from .plugin.musicplayer import vlc as player
            except SystemError:
                from plugin.musicplayer import vlc as player
        if song_source == 'youtube':
            try:
                from .plugin.songsource import youtube as source
            except SystemError:
                from plugin.songsource import youtube as source
        self.music_player = player.MusicPlayer(CFG)
        
        song_source = source.MusicSource(CFG)
        self.check_plugin_compatibility(self.music_player, song_source)
        # Open player and save the pid
        cmd = self.music_player.start()
        process = subprocess.Popen(cmd, shell=True)
        self.music_player.pid = process.pid
        
        if CFG['playing']['interface'] == 'http':
            def http(arg):
                port = CFG['playing']['port']
                if os.name == 'nt':
                    cmd = 'echo \"{0}\" | ncat localhost {1}'.format(arg,port)
                else:
                    cmd = 'echo \"{0}\" | nc localhost {1}'.format(arg,port)
                #~ print(cmd)
                subprocess.Popen(cmd, shell=True)
            self.music_player.http = http    
        while 1:
            #~ print('1')
            try:
                #~ print('checking the queue')
                tracks = self.playlist_queue.get(block=False)
            except queue.Empty:pass
            else:
                print('Tracks Gotten from queue')
                for track in tracks:
                    print('track title in track',track.title)
                    # if not track path or url in database
                    #~ print('song source is getting track info')
                    hits = song_source.load(track)
                    #~ print('track info gotten!')
                    if type(hits) == str:   # a single argument or arument string (local dir)
                        self.music_player.add_track(hits)
                        TRACKS_NEXT.append(hits)
                    else:                           # a stream item
                        #~ for hit_result in hits:
                            # filter out cruddy results!
                        print('queued a hit')
                        self.music_player.add_track(hits[0])
                        self.music_player.http_play()
                        # save this in the database!
                        TRACKS_NEXT.append(hits[0])
            time.sleep(1)
        '''     
        When Genre Changed
        When A New User Adds Data how to minimze calculations   
        '''
        pass
    def check_plugin_compatibility(self, player, song_source):
        for pfeat in player.features:
            if pfeat in song_source.features:
                break
        else:
            raise AttributeError('Player or source with unsupported feautres')
    

if __name__ == '__main__':  
    #~ import sys
    #~ print(sys.argv)
    args = docopt(__doc__)
    #~ args = docopt(__doc__,argv=['new','testing','--test'])
    #~ args = docopt(__doc__,argv=['load','testing223'])
    #~ args = docopt(__doc__,argv=['list']) 
    # args = docopt(__doc__,argv=['play'])
    #~ args = docopt(__doc__,argv=['cfg'])  
    # pprint(args)
    # sys.exit()
    # if args['help']:
    #     print(args['help'])
    #     sys.exit()
    
    if args['new'] or args['load'] or args['play']:
        LOAD = True
        TEST = False
        if args['new']:
            LOAD = False
        if args['--test']:
            TEST=True
        if not args['play']:
            Party(load=LOAD, name=args['<name>'], timeout=args['--timeout'], profile=args['--profile'], test=TEST)
        else:
            Party(play=True, load=True, name=args['<name>'], timeout=args['--timeout'], profile=args['--profile'], test=TEST)
    elif args['export']:pass
    elif args['list']:
        db_utils.list_playlists(args['name'])
    elif args['cfg']:
        subprocess.call(['nano','config.conf'])
    else:
        print(__doc__)
    #~ elif args['-test']:pass
    #~ Party(new=True)
    #~ app = Party()
    sys.exit()
     
