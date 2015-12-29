'''
Loads stuff that our music player can deal with.
either a stream file or a location to a song on hard disk
'''

class SongSource():
    def load(self):
        raise NotImplementedError
