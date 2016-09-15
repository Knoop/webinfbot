from configparser import RawConfigParser
import sqlite3
import tweepy

class StreamListener(tweepy.StreamListener):

    def __init__(self, con, cur):
        super(StreamListener, self).__init__()

        self.con = con
        self.cur = cur
        self.num = 0

    def on_status(self, status):
        self.num += 1

        # Handle statuses that contain one or more unicode characters, since the default Windows command prompt can't handle them
        try:
            print(' > ' + status.text)
        except UnicodeEncodeError:
            print(' * Some status containing unicode characters. The database contains the actual status.')

        cur.execute('INSERT INTO status (status) VALUES (?)', (status.text,))
        con.commit()

        if self.num == 10:
            return False

    def on_error(self, status_code):
        if status_code == 420:
            print(' * Error: exceeded connection rate limit.')
            return false
        else:
            print('Error: ' + str(status_code))

def get_db(db_file):
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY, status TEXT NOT NULL)')
    con.commit()

    return con, cur

# Read config file for account info and app keys
def get_config(config_file):
    parser = RawConfigParser()
    parser.read(config_file)

    return parser._sections

# Authenticate app through OAuth
def get_api(config):
    auth = tweepy.OAuthHandler(config['keys']['consumer_key'], config['keys']['consumer_secret'])
    auth.set_access_token(config['keys']['access_token'], config['keys']['access_secret'])

    return tweepy.API(auth)
    
# Create a simple stream listener
def get_stream(api, con, cur):
    streamListener = StreamListener(con, cur)

    return tweepy.Stream(auth = api.auth, listener = streamListener)

if __name__ == '__main__':
    db_file = './webinfbot.db'
    config_file = './webinfbot.ini'

    try:
        con, cur = get_db(db_file)
        config  = get_config(config_file)
        api     = get_api(config)
        stream  = get_stream(api, con, cur)

        # Only receive statuses containing 'python'
        stream.filter(track = ['python'])

        con.close()
    except KeyError:
        print(' * Error: missing key. Are you sure you have the proper config file in the correct location? (' + config_file + ')')