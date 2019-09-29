#!/usr/bin/python3
# -*- coding: utf-8 -*-
from random import choice
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
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
        profile_url = 'https://www.instagram.com/{}/'.format(profile)
        results = []
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
            for node in metrics:
                node = node.get('node')
                if node and isinstance(node, dict):
                    results.append(node)
            time_difference = datetime.now() - datetime.fromtimestamp(int(results[0]['taken_at_timestamp']))
            print('{:<25s} posted {:>12s} ago'.format(profile, str(time_difference)))
        
        except:
            print("Trouble finding info for " + profile_url)

    def profile_page_last9_post_metrics(self, profile):
        profile_url = 'https://www.instagram.com/{}/'.format(profile)
        # print(profile)
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
            likes = []
            for ctr, node in enumerate(metrics):
                node = node.get('node')
                # print("{}.Comments: {}".format(ctr, node["edge_media_to_comment"]["count"]))
                # print("{}.Likes: {}".format(ctr, node["edge_media_preview_like"]["count"]))
                likes.append(node["edge_media_preview_like"]["count"])
                # print("====")
            likes.sort()
            print(profile, likes)

        except Exception as e:
            print("Trouble finding info for " + profile_url)

    def print_node(self, node):
        timestamp_taken = int(node["taken_at_timestamp"])
        timestamp_difference = datetime.now().timestamp() - timestamp_taken

        time = datetime.fromtimestamp(timestamp_taken)
        time_difference = datetime.now() - time
        print("Time: {}".format(time))
        print('Posted {:>12s} ago'.format(str(time_difference)))
        print('Posted {} secs ago'.format(str(timestamp_difference)))

        print("Comments: {}".format(node["edge_media_to_comment"]["count"]))
        print("Likes: {}".format(node["edge_media_preview_like"]["count"]))
        print("====")

    def tag_page_media(self, tag):
        tag_url = "https://www.instagram.com/explore/tags/{}/".format(tag)
        tot_media_likes = 0
        tot_top_likes = 0
        top_likes_list = []
        try:
            response = self.__request_url(tag_url)
            json_data = self.extract_json_data(response)
            with open('tags_{}.json'.format(tag), 'w') as f:
                json.dump(json_data, f)
            total_medias = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']["count"]
            print("Total Medias: {}".format(total_medias))
            medias = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']["edges"]
            for ctr, node in enumerate(medias):
                print("Media: {}".format(ctr))
                node = node.get('node')
                self.print_node(node)
                tot_media_likes += node["edge_media_preview_like"]["count"]

            top_posts = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_top_posts']["edges"]
            print("Total top Posts: {}".format(len(top_posts)))
            for ctr, node in enumerate(top_posts):
                print("Top: {}".format(ctr))
                node = node.get('node')
                self.print_node(node)
                tot_top_likes += node["edge_media_preview_like"]["count"]
                top_likes_list.append(node["edge_media_preview_like"]["count"])
            print('tot_media_likes:', tot_media_likes)
            print('tot_top_likes:', tot_top_likes)
            print('top_likes_list:', top_likes_list)
            return min(top_likes_list)
        except Exception as e:
            print(e)
            traceback.print_exc()
            print("Trouble finding info for " + tag_url)


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

if __name__ == '__main__':
    main()
