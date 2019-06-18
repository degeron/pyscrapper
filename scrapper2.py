"""Imports"""
import redditdatatypes.page as reddit_page
import redditdatatypes.post as reddit_post
import scrapper.json_loader as loader

"""Main func"""
if __name__ == '__main__':
    # read config with proxies adresses, UA
    # select subreddit by parsing args
    # create database for posts
    # read first and next pages as much as possible
    # parse each page for posts
    # add each post to database
    ###
    # for each post in database get list of users with commenters and author
    #   add each user to database
    #   add post to completed db as [post
    ###
    # for each user in database get list of submission posts with subreddit as filter
    # add each post to database
    #
    # for each user in database get list of comments with subreddit as filter
    # add each post to database

    posts_db=dict()
    #posts_db[user_id]=list(user1,user2,..,userN)

    page=first_page()
    pages_list=list()
    while not end:
        pages_list.append(page)
        page=page.next()
    for page in pages_list:
        posts=page.get_posts()
        for post in posts:
            posts_db[post.id]=post.get_users()
            processed_posts[post.id]=len(post.get_users())

