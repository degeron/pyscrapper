import json


class page:
    json_data = dict()
    posts = list()

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

    def get_json_posts(self):
        return self.posts

    def after(self):
        return self.json_data['data']['after']
