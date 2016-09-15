from configparser import RawConfigParser
import tweepy

class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

# Read config file for account info and app keys
def get_config(file_path):
    parser = RawConfigParser()
    parser.read(file_path)

    return parser._sections

# Authenticate app through OAuth
def get_api(config):
    auth = tweepy.OAuthHandler(config['keys']['consumer_key'], config['keys']['consumer_secret'])
    auth.set_access_token(config['keys']['access_token'], config['keys']['access_secret'])

    return tweepy.API(auth)

# Create a simple stream listener
def get_stream(api):
    streamListener = StreamListener()

    return tweepy.Stream(auth = api.auth, listener = streamListener)

if __name__ == '__main__':
    config = get_config('webinfbot.ini')
    api    = get_api(config)
    stream = get_stream(api)

    # Only receive statuses containing 'python'
    stream.filter(track = ['python'])