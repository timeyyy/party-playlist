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

import db_utils
import contribution_func

# TODO how to safely use a class instance across threads?

class PlaylistManager():
    '''keep track of tracks that are played and updates the database for us so the state is saved'''
    def __init__(self, app):
        self.app = app
        self.old_index = 0
        self.updated = False

    def reset_times_played(self):
        pass

    def mark_played(self, title, artist, album):
        '''marks a track as having been played succesfu;ly'''
        with db_utils.connected_db(db_utils.Playlist, os.path.join(self.app.path_collection, self.app.current_collection)):
            track = db_utils.Playlist.get(db_utils.Playlist == title)
            track.times_played += 1


    def get_tracks(self, amount):
        '''Returns tracks to be played, this returns results in chunks.
        Our orm is
        under the hood rescans the playlist to see if updates have been made,
        remembers its position'''
        assert type(amount) == int or amount == 'all'
        if amount == 'all':
            amount = 30000
        tracks = []
        start = self.old_index
        end = start + amount
        with db_utils.connected_db(db_utils.Playlist, os.path.join(self.app.path_collection, self.app.current_collection)):
            #todo make it order also by the times played field
            #todo make it take into account if the playlist has been updated? is that required mm
            #what i do depends on how hard it is to delete playlist data from vlc...
            for i, track in enumerate(db_utils.Playlist.select().order_by(db_utils.Playlist.score)):
                if i >= start and i < end:
                    tracks.append(track)
                elif i == end:
                    self.old_index = i
                    break
        return tracks

    def list_tracks_in_playlist(self):
        for track in prev_tracks:
            print(track.title)
        for track in next_tracks:
            print(track.title)


    def monitor(self, play, song_source):
        # monitors our music player, takes care of
        # keeping track of which songs have been played succefully
        # fnding sources for music
        # updating sources and music player when playlist changes

        # if the playlists change...
        # reorganize the list if necessary
        # hold onto old streams incase the user presses previous..

        deque_lock = thread.allocate_lock()
        next_tracks = deque()
        prev_tracks = deque()
        def nexted_deque():
            with deque_lock:
                prev_tracks.appendleft(next_tracks.popleft())
        def preved_deque():
            with deque_lock:
                next_tracks.appendleft(prev_tracks.popleft())


        def skipped_or_completed(mode='unsure'):
            '''checks if a track was skipped or completed and marks it as so in the playlist'''
            assert mode in ('unsure', 'completed')


        def check_next_prev():
            '''this gets called when the user presses next or prev on the player
            if the track was listend to  90 % we mark it as complete, otherwise 
            we mark it as skipped
            the deques monitoring the tracks on the music player get updated as well'''
            while 1:
                action, track = self.app.music_player.next_prev_queue.get()
                if action == 'next':
                    nexted_deque()
                elif action == 'prev':
                    preved_deque()
                skipped_or_completed(track)

        thread.start_new_thread(check_next_prev, ())

        def remove_completed_songs_from_deque(lock):
            while 1:
                track = self.app.music_player.finished_playing_track()
                if track:
                    nexted_deque()
                    skipped_or_completed(track, mode='completed')
                time.sleep(5)

        thread.start_new_thread(remove_completed_songs_from_deque, ())


        def collection_updated():
            '''removes all besides the current song from our player and from our queue'''
            # when a user has pushed a contribution updating the collection, or collection settings have been trigged
            with suppress(AttributeError):
                if self.app.collection_updated:
                    del next_tracks[:-1]
                    # self.music_player.delete()
                    return True

        def block_until_we_can_add():
            while 1:
                if collection_updated():
                    return
                time.sleep(1)

        tracks = self.get_tracks()
        while 1:
            if collection_updated():
                tracks = self.get_tracks()
            else:
                block_until_we_can_add()
                tracks = self.get_tracks()
            if tracks:
                for track in tracks:
                    if collection_updated():
                        break
                    try:
                        logging.info('looking for song sources for {0} - {1}'.format(track.title, track.artist))
                        results = song_source.load(track)
                    except ConnectionError:
                        #TODO handle this problerly
                        logging.warning('Connection Error to internet')
                        print('Connection Error...')
                        return
                    if type(results) == str:   # a single argument or arument string (local dir)
                        self.app.music_player.add_track(results)
                        next_tracks.append(results)
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
                            next_tracks.append(track)

            # todo also check a queu if other ppl want to stop playing/continue playing.. and change thits accordingly
            if play:
                time.sleep(1)
                self.app.music_player.play()


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
    with open("config.conf", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg


def test():
    '''testing adding a new contribution to a playlist'''

'''

'''
if __name__ == '__main__':
    p = Prompt()
