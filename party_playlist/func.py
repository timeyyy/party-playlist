import os
import time
import sys
from collections import deque
from contextlib import suppress
import _thread as thread
import logging

from requests.exceptions import ConnectionError
import yaml
from timstools import silence
with silence():
    import blessed
if os.name == 'nt':
    import colorama
    from termcolor import colored

from party_playlist import db_utils
from party_playlist import contribution_func

# TODO how to safely use a class instance across threads?

class PlaylistManager():
    '''keep track of tracks that are played and updates the database for us so the state is saved'''
    def __init__(self, app):
        self.app = app
        self.old_index = 0
        self.updated = False
        self.deque_lock = thread.allocate_lock()
        self.next_tracks = deque()
        self.prev_tracks = deque()

    def start(self, play, song_source):
        thread.start_new_thread(self.check_next_prev, ())
        thread.start_new_thread(self.remove_completed_songs_from_deque, ())
        thread.start_new_thread(self.load_music, ())

    def check_next_prev(self):
        '''this gets called when the user presses next or prev on the player
        if the track was listend to  90 % we mark it as complete, otherwise
        we mark it as skipped
        '''
        while 1:
            action, track = self.app.music_player.next_prev_queue.get()
            if action == 'next':
                self.nexted_deque()
            elif action == 'prev':
                self.preved_deque()
            self.skipped_or_completed(track)


    def load_music(self, play, song_source):
        '''
        finds sources for music updating music player when required
        if the playlists change...
         - reorganize the list if necessary
         - holds onto old streams incase the user presses previous..
        '''

        tracks = self.get_tracks()
        while 1:
            if self.collection_updated():
                tracks = self.get_tracks()
            else:
                self.block_until_we_can_add()
                tracks = self.get_tracks()
            if tracks:
                for track in tracks:
                    if self.collection_updated():
                        break
                    else:
                        self.smash_that_record_on_baby()

            # todo also check a queu if other ppl want to stop playing/continue playing.. and change thits accordingly
            if play:
                time.sleep(1)
                self.app.music_player.play()

    def smash_that_record_on_baby(self, song_source, track):
        '''
        Loads a song from a song source and makes sure its the correct stream,
        TODO Does some caching of the stream and records if it was the correct one
        Then puts them on the playlist
        '''
        try:
            logging.info('looking for song sources for {0} - {1}'.format(track.title, track.artist))
            results = song_source.load(track)
        except ConnectionError:
            #TODO handle this properly!
            logging.warning('Connection Error to internet')
            print('Connection Error...')
            return
        if type(results) == str:   # a single argument or arument string (local dir)
            self.app.music_player.add_track(results)
            self.next_tracks.append(results)
        else:                           # a stream itemk
            # TODO FALL BACK ONTO HARDRIVE...
            # Todo save this in the database or keep a server hosted database of best sources?? mm ?
            # TODO filter out cruddy results!
            try:
                self.app.music_player.add_track(results[0])
                # can take a while to add the track over the network
            except IndexError:
                pass
            else:
                self.next_tracks.append(track)



    def reset_times_played(self):
        pass

    def mark_played(self, title, artist, album):
        '''marks a track as having been played succesfully'''
        with db_utils.connected_db(db_utils.Playlist, os.path.join(self.app.path_collection, self.app.current_collection)):
            track = db_utils.Playlist.get(db_utils.Playlist == title)
            track.times_played += 1


    def get_tracks(self):
        '''Returns tracks to be played.'''
        def generator_make():
            with db_utils.connected_db(db_utils.Playlist, os.path.join(self.app.path_collection, self.app.current_collection)):
                #todo make it order also by the times played field
                #todo make it take into account if the playlist has been updated? is that required mm
                #what i do depends on how hard it is to delete playlist data from vlc...
                for i, track in enumerate(db_utils.Playlist.select().order_by(db_utils.Playlist.score)):
                    yield track
        return generator_make()

    def list_tracks_in_playlist(self):
        #Todo use coroutine and pass in method to run... e.g printer etc
        for track in self.prev_tracks:
            print(track.title)
        for track in self.next_tracks:
            print(track.title)


    def nexted_deque(self):
        with self.deque_lock:
            self.prev_tracks.appendleft(self.next_tracks.popleft())
    def preved_deque(self):
        with self.deque_lock:
            self.next_tracks.appendleft(self.prev_tracks.popleft())


    @staticmethod
    def skipped_or_completed(mode='unsure'):
        '''checks if a track was skipped or completed and marks it as so in the playlist'''
        assert mode in ('unsure', 'completed')


    def remove_completed_songs_from_deque(self):
        '''also records the tracks completion state'''
        while 1:
            track = self.app.music_player.finished_playing_track()
            if track:
                self.nexted_deque()
                self.skipped_or_completed(track, mode='completed')
            time.sleep(5)


    def collection_updated(self):
        '''removes all besides the current song from our player and from our queue'''
        # when a user has pushed a contribution updating the collection, or collection settings have been changed
        with suppress(AttributeError):
            if self.app.collection_updated:
                del self.next_tracks[:-1]
                # self.music_player.delete()
                return True

    def block_until_we_can_add(self):
        while 1:
            if self.collection_updated():
                return
            time.sleep(1)


class Prompt():
    class Commands(dict):
        def add(self, function, cmd, *aliases):
            '''for registering commands for get_input above'''
            self[cmd] = function
            if aliases:
                for alias in aliases:
                    self[alias] = function

    def __init__(self, app):
        self.app = app
        self.heading ='green'
        self.warning = 'red'
        self.normal = 'normal'
        if os.name == 'nt':
            colorama.init()
        self.t = blessed.Terminal()

        # with self.t.fullscreen():
        self.p0()

    def p0(self):
        lines = (('Add a contribution', 'p1'),
                 ('Go to player interface...', 'music_player_interface'),
                 )
        self.page(lines,
                  header='Press a number to enter a command, q to quit!',
                  quit=sys.exit)

    def p1(self):
        self.clear()
        contribution_func.list_contribution(self.app.path_my_contribution)
        num = int(input())
        for i, contribution in enumerate(contribution_func.get_contributions(self.app.path_my_contribution)):
            if i == num:
                contribution_func.push_contribution(self.app.path_my_contribution,
                                            contribution=contribution,
                                            output_path=self.app.path_other_contribution,
                                            collection_path=self.app.path_collection,
                                            collection=self.app.current_collection,
                                            push_method='test')
                break
        else:
            self.colored_text('Couldn\'t find contribution..', color=self.warning)

        # give it time for the thread to start working on it..
        time.sleep(5)
        with self.app.BUSY:
            print('lock... acquired...exiting...')
            time.sleep(5)
            pass

    def music_player_interface(self):
        def help():
            self.clear()
            self.colored_text('Help Menu', color=self.heading)
            self.colored_text('next or n - Go to next track ', color=self.normal)
            self.colored_text('prev or p - Go to previous track ', color=self.normal)
            self.colored_text('play - start playing if paused or stopped ', color=self.normal)
            self.colored_text('pause - pause playing of tracks', color=self.normal)
            self.colored_text('playlist - show list of tracks on the playlist', color=self.normal)
            self.colored_text('q - quit out of this interface', color=self.normal)

        def test():
            self.app.music_player.finished_playing_track()

        self.clear()
        commands = self.Commands()
        self.colored_text('Music Player, h for list of commands', color=self.heading)
        commands.add(self.app.music_player.next, 'next', 'n')
        commands.add(self.app.music_player.prev, 'prev', 'p', 'previous')
        commands.add(self.app.music_player.play, 'play')
        commands.add(self.app.music_player.pause, 'pause')
        commands.add(self.app.music_player.add, 'add')
        commands.add(self.app.playlist_manager.list_tracks_in_playlist, 'playlist')
        commands.add(self.p0, 'quit', 'q')
        commands.add(help, 'help', 'h')
        commands.add(test, 'test', 't')
        self.get_command_input(break_after_command=False, **commands)

    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    def page(self, lines, header=None, clear_before=True, quit=False):
        '''prints a page of options for the cli, usefull if u want numbers to select an option'''
        commands = self.Commands()
        if clear_before:
            self.clear()
        if header:
            self.colored_text(header, color=self.heading)
        for i, line_and_callback in enumerate(lines):
            self.colored_text(text=' '+str(i+1)+' ',
                              norm_text=line_and_callback[0],
                              color='magenta')
            commands.add(function=line_and_callback[1],
                         cmd=str(i+1))
        if quit:
            commands.add(quit, 'quit', 'q')

        self.get_command_input(**commands)


    def colored_text(self, text, norm_text='', color='white', highlight=''):
        if os.name == 'nt':
            if not norm_text:
                if highlight:
                    print(colored(text, color, highlight))
                else:
                    print(colored(text, color))
            else:
                if highlight:
                        print(colored(text, color, highlight) + norm_text)
                else:
                    print(colored(text, color) + norm_text)
        else:
            if highlight:
                t_color = getattr(self.t, color+'_on_'+highlight)
                print('{color}{text}{t.normal}{norm_text}'.format(t=self.t,
                                                                  text=text,
                                                                  norm_text=norm_text,
                                                                  color=t_color))

            else:
                t_color = getattr(self.t, color)
                print('{color}{text}{t.normal}{norm_text}'.format(t=self.t,
                                                                    text=text,
                                                                    norm_text=norm_text,
                                                                    color=t_color))



    def get_command_input(self, on_false=lambda:0, break_after_command=True, **commands):
        ''' on false is a command to be run when a false command is input
        pass keys and commands that will be called when the user enters that command,
        methods can be passed in as strings or functions to be run'''
        while 1:
            try:
                data = input()
            except (KeyboardInterrupt, EOFError):
                return
            except IOError:
                data = 0 # unfortunaley input fucks up when uswing pdb sometimes i think XD TODO delete

            if commands.get(data):
                try:
                    commands[data]()
                except TypeError:
                    method = getattr(self, commands[data])
                    method()
                if break_after_command:
                    break
            else:
                on_false()


def get_config():
    with open(os.path.abspath('config.conf'), 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg


def test():
    '''testing adding a new contribution to a playlist'''

'''

'''
if __name__ == '__main__':
    p = Prompt()
