#!/usr/bin/python3
# -*- coding: utf-8 -*-
from random import choice
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
import dateparser
import os

import pprint as pp
import json
import traceback

_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
]

class InstagramScraper:
 
    def __init__(self, user_agents=None, proxy=None):
        self.user_agents = user_agents
        self.proxy = proxy
 
    def __random_agent(self):
        if self.user_agents and isinstance(self.user_agents, list):
            return choice(self.user_agents)
        return choice(_user_agents)
 
    def __request_url(self, url):
        try:
            response = requests.get(url, headers={'User-Agent': self.__random_agent()}, proxies={'http': self.proxy,
                                                                                                 'https': self.proxy})
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError('Received non 200 status code from Instagram')
        except requests.RequestException:
            raise requests.RequestException
        else:
            return response.text
 
    @staticmethod
    def extract_json_data(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.find('script')
        raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
        return json.loads(raw_string)
 
    def profile_page_metrics(self, profile_url):
        results = {}
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            with open('profile_page_metrics.json', 'w') as f:
                json.dump(json_data, f)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
        except Exception as e:
            raise e
        else:
            for key, value in metrics.items():
                if key != 'edge_owner_to_timeline_media':
                    if value and isinstance(value, dict):
                        value = value['count']
                        results[key] = value
                    elif value:
                        results[key] = value
        return results
 
    def profile_page_recent_posts_time(self, profile):
        profile_url = 'https://www.deskgram.cc/{}/'.format(profile)
        results = []
        try:
            response = self.__request_url(profile_url)
            soup = BeautifulSoup(response, 'html.parser')
            body = soup.find('body')
            time_elems = body.find_all('span', {"class": "time"})#, _class="time")
            times = [t.text for t in time_elems]
            time_difference = datetime.now() - dateparser.parse(times[0])
            print('{:<25s} posted {:>12s} ago'.format(profile, str(time_difference)))
        except Exception as e:
            print("Trouble finding info for " + profile_url)

def main():
    obj = InstagramScraper()
    dropbox_dir = "/Users/ishandutta2007/Dropbox"
    arr = os.listdir(dropbox_dir)
    username_list = []
    for a in arr:
        if "zzz" not in a and "yyy" not in a and "DS_Store" not in a:
            username_list.append(a)
    for x in username_list:
        obj.profile_page_recent_posts_time(x)

    # tag_list = ['virat']
    # for x in tag_list:
    #     obj.tag_page_media(x)

if __name__ == '__main__':
    main()
