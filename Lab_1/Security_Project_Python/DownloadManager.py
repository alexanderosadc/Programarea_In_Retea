import concurrent
from pprint import pprint
from concurrent import futures
from PubSub import events

from pip._vendor import requests


class DownloadManager:

    def __init__(self, base_url, register_url):
        self.base_url = base_url
        self.register_url = register_url
        self.headers = {
            'X-Access-Token': self.get_token()
        }

    def get_token(self):
        response = requests.get(url=self.register_url)
        response_json = response.json()
        return response_json['access_token']

    def access_root(self):
        self.headers['X-Access-Token'] = self.get_token()
        response = requests.get(url=self.base_url + "/home", headers=self.headers)
        links_from_json = self.get_links_from_json(response.json())

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.collect_links, links_from_json)
        events.publish("download_ended", results)

    def get_links_from_json(self, json):
        links_from_json = []

        if 'link' in json:
            for item in json['link']:
                links_from_json.append(json['link'][item])
            return links_from_json

    def collect_links(self, link):
        response = requests.get(self.base_url + link, headers=self.headers)
        response_json = response.json()
        links_from_json = self.get_links_from_json(response.json())
        if links_from_json:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(self.collect_links, links_from_json)
        else:
            results = []

        if 'mime_type' in response_json:
            data_to_send = [(response_json['data'], response_json['mime_type'])]
        else:
            data_to_send = [(response_json['data'], 'json')]

        data_to_send.extend(results)
        return data_to_send