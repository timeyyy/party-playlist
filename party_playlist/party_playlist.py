#~ from __future__ import print_function
#~ from __future__ import with_statement
#http://docopt.org/
__doc__ ="""Party Playlist
Usage:
    party_playlist.py new <name> [--timeout --profile --test]
    party_playlist.py load <name> [--timeout]
    party_playlist.py play [name] [--profile]
    party_playlist.py collection [list | -l] [<name>]
    party_playlist.py collection (delete | -d) <name>
    party_playlist.py contribution [list | -l | -n] [<name>]
    party_playlist.py contribution (delete | -d) <name>
    party_playlist.py export <name>
    party_playlist.py cfg
    party_playlist.py [-t | --test]
    party_playlist.py [-h | --help]

Options:
    new <name>  Create a new collection and start listening for new users
    load <name> Loads a previously created list, use timeout to control how long to set it active
    play [name] Play a playlist, defaults to last played
    collection list [name] Either list all playlists or enter the name or id of the playlist to view specifics
    collection delete <name>
    -t --test   testing mode will create if doesnt exists, and just load if it does
    -h --help   Show this screen and exit
"""
import time
import yaml
import _thread as thread
import queue
from collections import deque
import subprocess
import sys
import os
import logging
from contextlib import suppress

#~ import nxppy
import apptools

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:pass
from docopt import docopt

try:
    from . import func
    from . import db_utils
    from . import contribution_func
    from . import collection_func
    from . import process_tracks
except SystemError:
    import func
    import db_utils
    import contribution_func
    import collection_func
    import process_tracks

#user editable config
with open("config.conf", 'r') as ymlfile:
    CFG = yaml.load(ymlfile)

TRACKS_PREV = deque()
TRACKS_NEXT = deque()

APP_NAME = 'uncrumpled'
GENERAL_CFG_FILE = 'flags.cfg'
LOG_FILE = 'latest.log'

LOG_UPDATER_USERNAME = 'log_updater'
LOG_UPDATER_PASSWORD = 'updateing1!Hthefriggenlogs'
LOG_UPDATER_HOST = 'ftp.dynamicnotetaking.com'
LOG_UPDATER_PORT = 2222

DEVELOPING = True


class PartyPlaylist(apptools.AppBuilder):
    '''Manages the application lol, such as deciding if we
    are running for the first time, running on mobile or pc etc'''
    def  __init__(self):
        apptools.AppBuilder.__init__(self, name=APP_NAME)

    def start(self, **party_args):
        self.create_cfg(GENERAL_CFG_FILE)
        self.setup_paths()

        if self.first_run:
            db_utils.create_blank_db()

        args = docopt(__doc__)
        #~ args = docopt(__doc__,argv=['new','testing','--test'])

        # Normalize the args...
        if args.get('-d') or args.get('delete'):
            args['-d'] = True
            args['delete'] = True
        else:
            args['-d'] = False
            args['delete'] = False
        if args.get('-l') or args.get('list'):
            args['-l'] = True
            args['list'] = True
        else:
            args['-l'] = False
            args['list'] = False
        if args.get('-h') or args.get('help'):
            args['-h'] = True
            args['help'] = True
        else:
            args['-h'] = False
            args['help'] = False
        if args.get('-t') or args.get('test'):
            args['-t'] = True
            args['--test'] = True
        else:
            args['-t'] = False
            args['--test'] = False
        # if args.get('-n') or args.get('new'):
        #     args['-n'] = True
        #     args['new'] = True
        # else:
        #     args['-n'] = False
        #     args['new'] = False

        if args['new'] or args['load'] or args['play']:
            LOAD = True
            if args['new']:
                LOAD = False
            if not args['play']:
                Party(app=self, load=LOAD, name=args['<name>'], timeout=args['--timeout'], profile=args['--profile'], test=args['--test'], **party_args)
            else:
                Party(app=self, play=True, load=True, name=args['<name>'], timeout=args['--timeout'], profile=args['--profile'], test=args['--test'], **party_args)
        elif args['export']:pass
        elif args['collection']:
            if not args['delete']:
                # if args['<name>'] == '-l' or args['<name>'] == 'list':
                collection_func.list_collection(collection_path=self.path_collection, collection=args['<name>'])
                # else:
                #     collection_func.list_collection(args['<name>'])
            else:
                collection_func.delete_collection(collection_path=self.path_collection, collection=args['<name>'])
        elif args['contribution']:
            if not args['delete']:
                if args['<name>'] in ('-l', 'list'):
                    print('listconritbutions')
                    # collection_func.list_contributions(args['<name>'])
                elif args['-n']:
                    print('new contribution')
                    contribution_func.FindMusic(app=self, device='pc', db_name=args['<name>'])
                else:
                    print('listing conritbutions')
                    #TODO
                    for contrib in contribution_func.get_contributions(self.path_my_contribution):
                        print(contrib)
                    # contribution_func.list_contributions(args['<name>'])
            else:
                print('del contribution')
                # contribution_func.delete_contribution(args['<name>'])
        elif args['cfg']:
            subprocess.call(['vim','config.conf'])
        # elif args['--test']:
        #     contributionk
        else:
            print(__doc__)
        #~ elif args['-test']:pass
        #~ Party(new=True)
        #~ app = Party()
        sys.exit()

    def setup_paths(self):
        if not self.is_installed():
            appdir = os.path.join(os.getcwd(), 'appdata')
        else:
            appdir = self.uac_bypass()
        self.path_collection = os.path.join(appdir, 'collections')
        self.path_my_contribution = os.path.join(appdir, 'contribution', 'mine')
        self.path_other_contribution = os.path.join(appdir, 'contribution', 'other')


class Party():
    # Different Playing modes, either via button press or online config
    # Mode 1 Default, is autonomous, uses the default settings to organize
    # a playlist and play the music,  a genre toggle, and a next button
    # Mode 2 only plays music actually found on devices, then stops. no Discovery mode
    
    # Need a way to choose music output, either hdmi, cable or plug and play
    
    # User can overide playlist by using app or web interface

    # Alot of the options for changing music player etc are saved in a cfg file which can be edited manually
    # or by the program
    
    def __init__(self, app, name, load=False, timeout=False, profile=False,test=False, play=False, stdin=True):
        #~ self.input_actions = {5:lambda:print(5),7:None,12:None}
        #self.check_buttons()       # Buttons change the playback mode
        self.track_queue = queue.Queue()
        self.playlist_queue = queue.Queue()
        self.app = app
        thread.start_new_thread(self.setup_music_player,())

        self.current_collection = self.get_current_collection(name)

        if play:
            tracks = func.next_tracks(name, 3)
            self.playlist_queue.put(tracks)
            #~ tracks = func.next_tracks(name, 'all')
            #~ pprint(tracks)
            #~ print('adding')
        else:
            print("Party on, lets create a new/load existing collections")
            # Check Server for wifi and for nfc connections

            thread.start_new_thread(self.find_new_tracks,())
            # Run algo on tracks to make/edit the playlist
            thread.start_new_thread(self.playlist_from_tracks,(self.current_collection,load,timeout,profile))

        #handles input commands via commandline/stdin from user, for changing tracks etc
        if stdin:
            self.partyplaylist_input()

    def get_current_collection(self, name):
        '''returns the last userd playlist if none is given'''
        #TODO
        if name == None:
            name = 'testing'
            print('Selecting the last used playlist {0}'.format(name))
        return name

    def check_buttons(self):     # Maps Input Pins to different actions
        prev_input = 0
        while 1:
            INPUTS = ((i , GPIO.input(i)) for i in (5,17,12)) #pins to check
            for pin, result in INPUTS:
                if result and not prev_input:
                    self.input_actions(pin)
                    prev_input = 1
                    break
            prev_input = 0
            time.sleep(0.05) #should help stop bouncing
    
    def find_new_tracks(self):
        '''new found tracks will be put into a database named after the user'''
        # add new track function will copy over the contribution in question,
        # then the contribution will be added to the playlist
        # all i do here is check the playlist/collection for the contribution list
        print()
        print('waiting for new tracks via nfc/wifi')
        being_worked_on = []
        while 1:
            with suppress(TypeError):
                for new_contribution in contribution_func.get_new_contributions(self.app.path_collection,
                                                                                self.current_collection):
                    if new_contribution not in being_worked_on:
                        print('putting new contribution on queue')
                        self.track_queue.put(new_contribution)
                        being_worked_on.append(new_contribution)
            time.sleep(1)
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


    def playlist_from_tracks(self, collection, load, timeout, profile):
        '''Runs algo on tracks that are recieved from users
        These tracks then wait on a queue to be played if in play mode'''
        collection_func.create_or_get_collection(collection_path=self.app.path_collection,
                                                              collection=collection,
                                                              load=load)
        if not collection:
            # Already exists
            sys.exit()

        while 1:
            try:
                new_contribution = self.track_queue.get(block=False)
            except queue.Empty:
                pass
            else:
                self.process_tracks(self.app.path_collection,
                                    collection,
                                    self.app.path_other_contribution,
                                    new_contribution,
                                    load,
                                    timeout,
                                    profile)
                # tracks = func.next_tracks(name, 2)
                # self.playlist_queue.put(tracks)
            time.sleep(0.5)

    def process_tracks(self, *args, **kwargs):
        process_tracks.process_tracks(*args, **kwargs)

    def partyplaylist_input(self):
        '''Blocks, reads commands from stdin and provides a simple api for common actions'''
        # a dict wrapper with one custom method
        commands = func.RegisterCommands()
        while 1:
            # keep looping until our plater is setup
            try:
                commands.add(self.music_player.http_next, 'next', 'n')
            except AttributeError:
                pass
            else:
                break
        commands.add(self.music_player.http_prev, 'prev', 'p', 'previous')
        commands.add(self.music_player.http_play, 'play')
        commands.add(self.music_player.http_pause, 'pause')
        commands.add(self.music_player.http_add, 'add')
        commands.add(func.test, 'test')

        func.get_input(**commands)


    def setup_music_player(self):
        '''Setup logic for MusicPlayer'''
        return
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
    if len(sys.argv) == 2 and sys.argv[1] == 'developing':
        DEVELOPING = True
    if DEVELOPING:
        sys.setrecursionlimit(100)

    app_framework_instance = apptools.AppBuilder(name=APP_NAME)
    LOG_FILE = app_framework_instance.uac_bypass(LOG_FILE)
    apptools.setup_logger(LOG_FILE)
    logging.info('Developer status is: %s' % DEVELOPING)
    try:
        main = PartyPlaylist()
        main.start()
    except Exception as err:
        apptools.handle_fatal_exception(restarter=app_framework_instance.app_restart,
                                        error=err,
                                        file=LOG_FILE,
                                        host=LOG_UPDATER_HOST,
                                        username=LOG_UPDATER_USERNAME,
                                        password=LOG_UPDATER_PASSWORD,
                                        port=LOG_UPDATER_PORT,
                                        )
    finally:
        main.shutdown()
        sys.exit()


'''
New Collectioin
    - Play during collection
    - create collection from old collection

Your Musiccontribution
    - new
        - tweak folders etc settings
    - edit
        - tweak rules, add / del
        - import from interent etc

Play collection
    - select settings on the fly and view list
    - export static playlist
'''
