__doc__ ="""Party Playlist
Usage:
    party_playlist.py load [<name>]
    party_playlist.py play [<name>] [--profile]
    party_playlist.py collection (new  | -n) [<name>]
    party_playlist.py collection (list | -l) [<name>]
    party_playlist.py collection (delete | -d) <name>
    party_playlist.py contribution (new | -n) [<name>] [--mode=<'spotify folders facebook'>] [--default_paths=<True/False>] [--paths=<'p1 p2 p3'>]
    party_playlist.py contribution [list | -l] [<name>]
    party_playlist.py contribution (delete | -d) <name>
    party_playlist.py export <name>
    party_playlist.py cfg
    party_playlist.py [-t | --test]
    party_playlist.py [-h | --help]

Options:
    load <name> Loads a previously created list, use timeout to control how long to set it active
    play [name] Play a playlist, defaults to last played
    collection list [name] Either list all playlists or enter the name or id of the playlist to view specifics
    collection delete <name>
    -t --test   testing mode will create if doesnt exists, and just load if it does
    -h --help   Show this screen and exit
"""
import time
import _thread as thread
import queue
import sys
import os
import logging
from contextlib import suppress
from time import strftime, gmtime
import pdb
from pprint import pprint

#~ import nxppy
import peewee
import peasoup

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

APP_NAME = 'uncrumpled'
GENERAL_CFG_FILE = 'flags.cfg'
LOG_FILE = 'latest.log'

LOG_UPDATER_USERNAME = 'log_updater'
LOG_UPDATER_PASSWORD = 'updateing1!Hthefriggenlogs'
LOG_UPDATER_HOST = 'ftp.dynamicnotetaking.com'
LOG_UPDATER_PORT = 2222

DEVELOPING = True

class PartyPlaylist(peasoup.AppBuilder):
    '''Manages the application lol, such as deciding if we
    are running for the first time, running on mobile or pc etc'''
    def  __init__(self):
        peasoup.AppBuilder.__init__(self, name=APP_NAME)

    def start(self, **party_args):
        self.create_cfg(GENERAL_CFG_FILE)
        self.setup_paths()
        self.setup_user_cfg()

        if self.first_run:
            db_utils.create_blank_db()

        self.mode = 'cli'
        if self.mode == 'cli':
            import cli
            args = docopt(__doc__)
            cli.start(app=self, args=args, Party=Party, **party_args)
        elif self.mode == 'gui':
            pass

    def setup_paths(self):
        if not self.is_installed():
            appdir = os.path.join(os.getcwd(), 'appdata')
        else:
            appdir = self.uac_bypass()
        self.path_collection = os.path.join(appdir, 'collections')
        self.path_my_contribution = os.path.join(appdir, 'contribution', 'mine')
        self.path_other_contribution = os.path.join(appdir, 'contribution', 'other')
    
    def setup_user_cfg(self):
        '''this is a user editable cfg file while the other is more for programmer use'''
        self.user_cfg = func.get_config()


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
        self.app.BUSY = thread.allocate_lock()
        self.app.current_collection = self.get_current_collection(name)

        self.setup_music_player(play)

        # if play:
            # tracks = self.app.playlist_manager.get_tracks(1)
            # if tracks:
            #     self.playlist_queue.put(tracks)
            #     tracks = self.app.playlist_manager.get_tracks('all')
            #     if tracks:
            #         self.playlist_queue.put(tracks)
        # Check Server for wifi and for nfc connections
        thread.start_new_thread(self.find_new_tracks,())
        # Run algo on tracks to make/edit the playlist
        thread.start_new_thread(self.playlist_from_tracks,(self.app.current_collection,load,timeout,profile))

        #handles input commands via commandline/stdin from user, for changing tracks etc
        if stdin:
            self.partyplaylist_input(load)

    def get_current_collection(self, name):
        '''returns the last userd playlist if none is given'''
        #TODO
        if name == None:
            name = strftime("testing %a, %d %b %Y %H-%M-%S.db", gmtime())
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
            with suppress(TypeError, peewee.OperationalError):
                for new_contribution in contribution_func.get_new_contributions(self.app.path_collection,
                                                                                self.app.current_collection):
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
                with self.app.BUSY:
                    self.process_tracks(self.app.path_collection,
                                        collection,
                                        self.app.path_other_contribution,
                                        new_contribution,
                                        self.app.user_cfg,
                                        profile)

                with suppress(AttributeError):
                    self.app.collection_updated = True
            time.sleep(0.5)

    def process_tracks(self, *args, **kwargs):
        process_tracks.process_tracks(*args, **kwargs)

    def partyplaylist_input(self, load):
        '''Blocks, reads commands from stdin and provides a simple api for common actions'''
        # a dict wrapper with one custom method
        if not load:
            while 1:
                # keep looping until our plater is setup
                try:
                   self.app.music_player.next
                except AttributeError:
                    pass
                else:
                    break
        prompt = func.Prompt(app=self.app)


    def setup_music_player(self, play):
        '''Setup logic for MusicPlayer'''
        player = self.app.user_cfg['playing']['music_player']
        song_source = self.app.user_cfg['playing']['song_source']
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
        self.app.music_player = player.MusicPlayer(self.app, self.app.user_cfg)
        song_source = source.MusicSource(self.app.user_cfg)
        self.check_plugin_compatibility(self.app.music_player, song_source)

        logging.info('starting our musicplayer!')
        self.app.music_player.launch()

        self.app.playlist_manager = func.PlaylistManager(app=self.app)
        thread.start_new_thread(self.app.playlist_manager.monitor,(play, song_source))

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
        sys.setrecursionlimit(175)

    app_framework_instance = peasoup.AppBuilder(name=APP_NAME)
    LOG_FILE = app_framework_instance.uac_bypass(LOG_FILE)
    peasoup.setup_logger(LOG_FILE)
    logging.info('Developer status is: %s' % DEVELOPING)

    MODE = 'cli'
    if MODE == 'cli':
        pre_restarter = lambda *args, **kwargs:0
        restarter = lambda *args, **kwargs:0
    else:
        pre_restarter = 'gui'
        restarter = app_framework_instance.app_restart

    try:
        main = PartyPlaylist()
        main.start()
    except Exception as err:
        peasoup.handle_fatal_exception(restarter=restarter,
                                        error=err,
                                        file=LOG_FILE,
                                        host=LOG_UPDATER_HOST,
                                        username=LOG_UPDATER_USERNAME,
                                        password=LOG_UPDATER_PASSWORD,
                                        port=LOG_UPDATER_PORT,
                                        pre_restarter=pre_restarter
                                        )
    finally:
        print('RUNNING SHUTDOWN')
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
