import yaml

def next_tracks(playlist_db_name, number):
    '''Returns tracks to be played!'''
    if number == 'all':
        number = 0.1    # will never equal this so for loop will grab all tracks
    #TODO make sure playlist_db_name is sanitzied etc
    db = db_utils.connect_db(Collection, playlist_db_name)
    tracks = []
    #~ PlayList.playlist_name = ''
    for i, track in enumerate(db_utils.PlayList.select().order_by(db_utils.PlayList.score)):
        if i == number:
            break
        tracks.append(track)
    return tracks

def get_input(on_false=lambda:0, **commands):
    ''' on false is a command to be run when a false command is input
    pass keys and commands that will be called when the user enters that comand'''
    while 1:
        try:
            data = input()
        except KeyboardInterrupt:
            return
        except IOError:
            data = 0 # unfortunaley input fucks up when uswing pdb sometimes i think XD TODO delete

        if commands.get(data):
            commands[data]()
        else:
            on_false()

class RegisterCommands(dict):
    def add(self, function, cmd, *aliases):
        '''for registering commands for get_input above'''
        self[cmd] = function
        if aliases:
            for alias in aliases:
                self[alias] = function

def get_config():
    with open("config.conf", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg





def test():
    '''testing adding a new contribution to a playlist'''

'''

'''
