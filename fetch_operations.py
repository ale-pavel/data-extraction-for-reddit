#!/usr/bin/env python3
import requests
from collections import deque
import mongo_operations
from time import sleep

# used to fetch every comment from a post, and persist it to MongoDB
def fetch_comments_from_post(post_id):
    response = requests.get("https://oauth.reddit.com/r/sanfrancisco/new",
                            headers=headers,
                            params=params)

    comment_tree = response.json()[1]['data']['children']
    # define a deque for better performance
    queue = deque(comment_tree)

    # loop through each comment obtained from a single post
    for comment in queue:
        # remove the current processed comment from the queue
        queue.popleft()

        comment_data = {
            '_id': comment['data']['id'],
            'parent': comment['data']['parent_id'],
            'kind': comment['kind'],
            'author': comment['data']['author'],
            'author_fullname': comment['data']['author_fullname'],
            'body': comment['data']['body'],
            'ups': comment['data']['ups'],
            'downs': comment['data']['downs']
        }

        post_id = comment['link_id']
        # persist the comment in mongoDB, in a collection identified by the post (each comment is a document)
        mongo_operations.persist_comment(comment_data, post_id)

        # get the replies list for the current comment
        replies = comment['replies']['data']['children']
        # add it to the queue (depth-first search), only if replies are present
        if replies != '' and len(replies) > 0:
            queue.appendleft(replies)


# we use this function to convert responses to a list of parsed posts
def post_list_from_response(response):
    post_list_batch = []

    # loop through each post pulled from response and append to a list
    for post in response.json()['data']['children']:
        post_data = {
            '_id': post['data']['id'],
            'kind': post['kind'],
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score']
        }

        post_list_batch.append(post_data)

        # don't overload the servers with requests
        sleep(1)
        # get and persist the comments for the current post
        fetch_comments_from_post(post['data']['id'])

    return post_list_batch
