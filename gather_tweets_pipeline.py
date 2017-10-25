# A pipeline for gathering tweets, removing non-ASCII characters, and saving to CSV file

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

import sys
import os
import json
import time
import datetime
import re

import pandas as pd



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
def main():
    # Key and token info needed
    consumer_key = 'B7hFHsvyI73nNLEr7uSoXS82v'
    consumer_secret = 'FhXkqeM5pnx7RgNGGFv3Uk1oczvtQRFEHD4DpiMRx1Q3mFXllP'
    access_token = '233007802-JU1p0xAisG1ZUc87d1FXVq4t5EfSzNPi9Axe8MU4'
    access_secret = 'hYPc7CYXkc1dhf9newqF4kyADMl4Uw4LuNRQaTcZDxGg9'

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    # Welcome
    print('===========================================================')
    print('Welcome to the user interface of gathering tweets pipeline!')
    print('You can press "Ctrl+C" at anytime to abort the program.')
    print('===========================================================')
    print()

    # Prompt for input keywords
    methods = ['manual', 'file']
    while True:
        m = input('How do you want to specify your key words?\nType "manual" or "file" >>> ')
        if m in methods:
            break
        else:
            print('\"{}\" is an invalid input! Please try again.\n'.format(m))

    # Choose keywords:
    if m == 'file':
        print('===========================================================')
        print('Please input the file name that contains your key words.')
        print('Notes:')
        print('    The file should contain key words in one or multiple lines, and multiple key words should be separated by *COMMA*.')
        print('        For example: NBA, basketball, Lebron James')
        print('    If the file is under the current directory, you can directly type the file name, e.g., "keywords.txt".')
        print('    If the file is in another directory, please type the full file name, e.g., "C:\\Downloads\\keywords.txt" (for Windows), or "/Users/xy/Downloads/keywords.txt" (for MacOS/Linux).')

        while True:
            file_name = input('Type your file name >>> ')
            if os.path.isfile(file_name):
                break
            else:
                print('"{}" is not a valid file name! Please check if the file exists.\n'.format(file_name))

        # Check the content of keywords file
        key_words = []
        with open(file_name, 'r') as f:
            lines = f.readlines()
            if len(lines) == 0:
                print('\n{} is an empty file!\nTask aborted!'.format(file_name))
                sys.exit(1)

            for line in lines:
                line = line.strip()
                # Detect non-ASCII characters
                for c in line:
                    if ord(c) >= 128:
                        print('\n{} contains non-ASCII characters: "{}" \nPlease remove them and try again'.format(file_name, c))
                        sys.exit(1)
                # Check delimiters
                if line.count(' ') > 1 and ',' not in line:
                    print('\nMore than 1 <space> symbols exist in the key words file, but none comma exists')
                    print('I\'m confused about your keywords. Please separate your key words by commas.')
                    sys.exit(1)

                words = line.split(',')
                for w in words:
                    if len(w.strip()) > 0:
                        key_words.append(w.strip())

        # Check key_words
        if len(key_words) == 0:
            print('\nZero key words are found in {}! Please check your key words file.'.format(file_name))
            sys.exit(1)

    elif m == 'manual':
        print('===========================================================')
        print('Please input your key words (separated by comma), and hit <ENTER> when done.')

        while True:
            line = input('Type the key words >>> ')
            line = line.strip()

            invalid_flag = False
            # Check empty
            if len(line) == 0:
                print('\nYour input is empty! Please try again.')
                invalid_flag = True
            # Detect non-ASCII characters
            for c in line:
                if ord(c) >= 128:
                    print('\nYour input contains non-ASCII characters: "{}"! Please try again.'.format(c))
                    invalid_flag = True
                    break
            # Check delimiters
            if line.count(' ') > 1 and ',' not in line:
                print('\nMore than 1 <space> symbols exist in your input, but none comma exists')
                print('I\'m confused about your keywords. Please try again')
                invalid_flag = True

            if invalid_flag:
                continue
            else:
                break

        # Process input
        key_words = []
        for w in line.split(','):
            if len(w.strip()) > 0:
                key_words.append(w.strip())

    # Print valid key words
    key_words = list(set(key_words))
    print('\n{} unique key words being used: '.format(len(key_words)), key_words)

    # Prompt for number of tweets to be gathered
    print('===========================================================')
    print('How many tweets do you want to gather? \nInput an integer number, or just hit <ENTER> to use the default number 300.')
    num_tweets = 300
    while True:
        s = input('Input an integer >>> ')
        s = s.strip()
        if len(s) == 0:
            break
        elif s.isdigit():
            num = int(s)
            if num > 0:
                num_tweets = num
                break
            else:
                print('\nPlease input a number that is greater than 0.')
        else:
            print('\nPlease input a valid integer number.')

    print('{} tweets to be gathered.'.format(num_tweets))

    # Streaming
    # TODO: remvoe '\t', '\n' and ',' in text field, also remove empty text
    print('===========================================================')
    print('Start gathering tweets ...')

    postfix = current_datetime_str()
    raw_file = 'raw_{}.json'.format(postfix)
    csv_file = 'data_{}.csv'.format(postfix)
    text_file = 'text_{}.csv'.format(postfix)

    twitter_stream = Stream(auth, MyListener(output_file=output_file))
    twitter_stream.filter(track=keywords)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nTask aborted!')
