#!/usr/bin/python
from typing import TextIO

import requests
import json
import time
from tinydb import TinyDB, Query

# requests setup
headers = {'User-agent': 'your bot 0.1'}
proxies = {
    'http': 'proxy.inn.intel.com:911',
    'https': 'proxy.inn.intel.com:912',
}
# proxies = None
subreddit = 'chastity'
jsn = '.json'


def load_data(url, proxies, headers):
    r = requests.get(url, proxies=proxies, headers=headers)
    if r.status_code != 200:
        raise Exception('Bad Response (%d %s) for url %s' % (r.status_code, r.reason, url))
    print('status = ', r.status_code)
    return json.loads(r.text), r.status_code


def save_to_file(data, filemask, page_num):
    posts_fn = filemask + '.' + subreddit + '.' + str(page_num) + jsn
    posts_file: TextIO = open('./' + filemask + '/' + posts_fn, 'w')
    posts_file.write(data)
    posts_file.close()


if __name__ == '__main__':
    posts_db = TinyDB('./posts.json')
    users_db = TinyDB('./users.json')
    comms_db = TinyDB('./comms.json')
    # url_setup
    _root = 'https://www.reddit.com/r/'
    # https://www.reddit.com/r/Art.json?sort=new&after=t3_bvq20s
    start_url = _root + subreddit + jsn + '?sort=new'
    # depth
    pages = 10
    url = start_url
    next_page = ""
    after = None
    # callcntr=0
    for page_num in range(pages):
        print('getting page #', page_num)
        if after:
            url = start_url + '&' + 'after=%s' % after
        print('url = ', url)
        page_data = load_data(url, proxies, headers)
        if page_data['data']['after'] == after:
            print('This page the same as previous')
            break
        # files with dump
        save_to_file(page_data, 'posts', page_num)
        if not page_data['kind'] == 'Listing':
            raise Exception('Invalid json data')
        after = page_data['data']['after']
        dist = page_data['data']['dist']
        print('total %d entries' % dist)
        print(len(page_data['data']['children']))
        for post in page_data['data']['children']:
            if post['kind'] != 't3':
                raise Exception('post is not t3')
            print(post['data']['id'], ' ', len(post['data']['selftext']))
            post['data']['post_len'] = len(post['data']['selftext'])
            posts_db.insert(post['data'])
        time.sleep(0.3)
    ###
    print('Collected %d posts' % len(posts_db))

    for post in posts_db:
        user_name = post['author']
        user_id = post['author_fullname']  # "author_fullname": "t2_3e5sqcif"
        post_id = post['id']
        print('parsing post %s by %s - %s' % (post_id, user_id, post['title']))
        User = Query()
        users_db.upsert({'user_id': user_id, 'user_name': user_name}, User.user_id == user_id)
        url = 'https://www.reddit.com/r/%s/comments/%s.json' % (subreddit, post_id)
        print('url = ', url)
        r = requests.get(url, proxies=proxies, headers=headers)
        time.sleep(0.3)
        if r.status_code != 200:
            raise Exception('Bad Response (%d %s) for url %s' % (r.status_code, r.reason, url))
        print('status = ', r.status_code)
        post_content = json.loads(r.text)
        # TODO add checks of kinds
        post_itself = post_content[0]['data']
        post_comment_objs = post_content[1]['data']['children']
        callcntr = 0
        for comment_obj in post_comment_objs:
            comment = comment_obj['data']
            comment_id = comment['id']
            comment_len = len(comment['body'])
            comment_author_id = comment['author_fullname']
            comment_author_name = comment['author']
            comment_url = comment['permalink']
            users_db.upsert({'user_id': comment_author_id, 'user_name': comment_author_name},
                            User.user_id == comment_author_id)
            comms_db.insert({
                'post_id': post_id,
                'comm_id': comment_id,
                'comm_len': comment_len
            })
    print('Collected %d comms' % len(comms_db))
    print('Collected %d usernames' % len(users_db))

    for user in users_db:
        print("analysing user ", user['user_name'])
        url = 'https://www.reddit.com/user/%s/comments.json' % user['user_name']
        r = requests.get(url, proxies=proxies, headers=headers)
        time.sleep(0.3)
        if r.status_code != 200:
            raise Exception('Bad Response (%d %s) for url %s' % (r.status_code, r.reason, url))
        print('status = ', r.status_code)
        usercomments_content = json.loads(r.text)
        total_comms = usercomments_content['data']['dist']
        user_comments = usercomments_content['data']['children']
        print('User have %d comments' % len(user_comments))
        sub_comm_cntr = 0
        for user_comment_obj in user_comments:
            user_comment = user_comment_obj['data']
            if user_comment['subreddit'] == subreddit:
                sub_comm_cntr += 1
        print('User have %d comments for subreddir %s' % (sub_comm_cntr, subreddit))
