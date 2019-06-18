import json


class post:
    json_data = dict()
    users = list()
    comms = list()
    id=-1

    def __init__(self, data):
        self.json_data = data
        if not self.json_data['kind'] == 'Listing':
            raise Exception('Invalid json data')
        for post in self.json_data['data']['children']:
            if post['kind'] != 't3':
                raise Exception('post is not t3')
            self.posts.append(post)

    def get_json(self):
        return self.json_data

    def get_json_comms(self):
        return self.comms

    def id(self):
        return self.json_data['data']['id']
