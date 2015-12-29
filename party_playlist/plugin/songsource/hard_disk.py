
import os

from party_playlist.plugin.songsource import SongSource
from party_playlist import contribution_func

class MusicSource(SongSource):
    def __init__(self, cfg):
        self.features = ('local',)

        finder = Finder()
        import pdb;pdb.set_trace()
        print(cfg['playing']['paths'])
        # if cfg['playing']['paths']:
        #     folders = finder.folders() =
        default_paths = []

    def load(self, track):
        pass
        # path
        # if self.cfg['playing']

class Finder(contribution_func.FindMusic):
    '''
    Hack into the finder so instead of finding tracks it gives us paths, useful because
    we get all the default paths for free
    '''
    def _folders(self, *paths):
        extens = ('.mp3', '.wav', '.wma', '.ra', '.rm', '.ram', '.mid', '.ogg', '.aac', '.m4a', '.alac', '.ape',
                  '.flac', '.aiff')
        for path in paths:
            for root, dirs, files in os.walk(path):
                song_paths = [os.path.join(root, file) for file in files if os.path.splitext(file)[-1] in extens]
                if song_paths:
                    for song_path in song_paths:
                        song_info = hsaudiotag.auto.File(song_path)
                        self.add(song_info, source='hard_disk')
