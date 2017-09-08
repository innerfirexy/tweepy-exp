# Use tweepy package to download

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import sys
import os
import json
import time
import datetime


# Key and token info needed
consumer_key = 'B7hFHsvyI73nNLEr7uSoXS82v'
consumer_secret = 'FhXkqeM5pnx7RgNGGFv3Uk1oczvtQRFEHD4DpiMRx1Q3mFXllP'
access_token = '233007802-JU1p0xAisG1ZUc87d1FXVq4t5EfSzNPi9Axe8MU4'
access_secret = 'hYPc7CYXkc1dhf9newqF4kyADMl4Uw4LuNRQaTcZDxGg9'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)


# Define the listener
class MyListener(StreamListener):
    def __init__(self, max_num=300, output_file='my_tweets.json'):
        super().__init__()
        self.max_num = max_num
        self.output_file = output_file
        self.count = 0
        self.start_time = time.time()

    def on_data(self, data):
        if data.startswith('{"limit":'):
            return
        # tweet = json.loads(data)
        # if 'retweeted_status' in tweet:
        #     return

        with open(self.output_file, 'a') as f:
            f.write(data)
            # Increment count
            self.count += 1
            # if self.count % 10 == 0 and self.count > 0:
            print('{}/{} tweets downloaded'.format(self.count, self.max_num))

            # Check if reaches the maximum tweets number limit
            if self.count == self.max_num:
                print('Maximum number reached, aborting.')
                end_time = time.time()
                elapse = end_time - self.start_time
                print('It took {} seconds to download {} tweets'.format(elapse, self.max_num))
                sys.exit(0)

    def on_error(self, status):
        print(status)
        return True


# Get the str representation of the current date and time
def current_datetime_str():
    return f'{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}'


# Main
if __name__ == '__main__':
    # Parse arguments
    keywords = sys.argv[1:]

    if len(keywords) == 0:
        print('You did not provide any key words')
    else:
        print('Downloading tweets for key words: ', keywords)
        output_file = 'my_tweets_{}.json'.format(current_datetime_str())
        
        twitter_stream = Stream(auth, MyListener(output_file=output_file))
        twitter_stream.filter(track=keywords)
