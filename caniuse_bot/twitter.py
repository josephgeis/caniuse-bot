from typing import Dict, Union, List
import requests
from requests_oauthlib import OAuth1
import re
import os
import time
import threading
from dotenv import load_dotenv
import logging

from .formatter import generate_tweet

load_dotenv()

USERNAME = os.environ["TWITTER_USERNAME"]
API_KEY = os.environ["TWITTER_API_KEY"]
API_SECRET = os.environ["TWITTER_API_SECRET"]
TOKEN = os.environ["TWITTER_TOKEN"]
SECRET = os.environ["TWITTER_SECRET"]
START_SINCE = os.environ.get("START_SINCE", 1)

auth = OAuth1(API_KEY, API_SECRET, TOKEN, SECRET)

pattern = re.compile(fr"@{USERNAME} !!\s?([\x20-\x7E]+)")


def get_mentions(since: Union[int, None]) -> Dict:
    commands = []

    mentions = requests.get(
        "https://api.twitter.com/1.1/statuses/mentions_timeline.json",
        params={
            "since_id": since or 1,
            "count": 200,
            "include_rts": 0
        },
        auth=auth).json()

    if not mentions:
        return None

    for mention in mentions:
        if pattern.match(mention["text"]):
            commands.append(mention)

    return {"last_id": mentions[0]['id'], "commands": commands}


def post_tweet(command):
    match = pattern.match(command['text'])
    username = command['user']['screen_name']
    tweet_id = command['id_str']

    r = requests.post("https://api.twitter.com/1.1/statuses/update.json",
                      params={
                          "status": generate_tweet(match.group(1), username),
                          "in_reply_to_status_id": tweet_id,
                      },
                      auth=auth)


def process_commands(commands: List[Dict]):
    for command in commands:
        threading.Thread(target=post_tweet, args=[command]).run()


if __name__ == "__main__":
    logging.basicConfig(
        filename='caniuse.log',
        level=logging.DEBUG,
        format='%(asctime)s | %(name)s | %(levelname)s || %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
    since = START_SINCE
    logging.info(f"Starting Twitter watcher with mention {since}")
    while True:
        logging.info("Updating mentions")
        ment_seach = get_mentions(since)
        if ment_seach:
            since = ment_seach['last_id']
            logging.info(f"Set last mention to {since}")
            process_commands(ment_seach['commands'])
            logging.info(f"Got {len(ment_seach['commands'])} commands.")
        time.sleep(20)
