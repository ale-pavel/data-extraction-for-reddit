#!/usr/bin/env python3
import requests
from collections import deque
import mongo_operations
from time import sleep

# POST_LIMIT = 5
COMMENT_LIMIT = 50


# used to fetch every comment from a post, and persist it to MongoDB
def fetch_comments_from_post(post_id, headers):
    params = {'limit': COMMENT_LIMIT}
    response = requests.get(f"https://oauth.reddit.com/r/sanfrancisco/comments/{post_id}",
                            headers=headers,
                            params=params)

    comment_tree = response.json()[1]['data']['children']
    # define a deque for better performance
    queue = deque(comment_tree)
    i = 0

    # loop through each comment obtained from a single post
    while queue:
        # remove the current processed comment from the queue
        comment = queue.popleft()
        # comment limit number has been reached, load more
        if comment['kind'] == 'more':
            print('MORE Comments')
            more_list = ','.join(comment['data']['children'])
            comment_list = get_more_comments(post_id, more_list, headers)
            queue.extendleft(comment_list)
        else:
            comment_data = {
                '_id': comment['data']['id'],
                'parent': comment['data']['parent_id'],
                'kind': comment['kind'],
                'author': comment['data']['author'],
                'body': comment['data']['body'],
                'ups': comment['data']['ups'],
                'downs': comment['data']['downs'],
                'post_id': comment['data']['link_id']
            }

            if comment['data']['author'] != '[deleted]':
                comment_data['author_fullname'] = comment['data']['author_fullname']
            post_id = comment['data']['link_id']
            # persist the comment in mongoDB, in a collection identified by the post (each comment is a document)
            mongo_operations.persist_comment(comment_data, post_id)

            # get the replies list for the current comment
            replies = comment['data']['replies']
            # add it to the queue (depth-first search), only if replies are present
            if replies != '' and len(replies['data']['children']) > 0:
                queue.extendleft(replies['data']['children'])

            i += 1
            print(f'comment tree processed (post {post_id} - {i} comments)')


# get all the remaining comments following a "more"-kind comment returned
def get_more_comments(post_id, more_comments, headers):
    params = {'api_type': 'json',
              'children': more_comments,
              'limit_children': False,
              'link_id': post_id,
              'sort': 'new'}
    response = requests.get(f"https://oauth.reddit.com/api/morechildren",
                            headers=headers,
                            params=params)
    response_json = response.json() # for debugging
    try:
        comments_list = response.json()['json']['data']['things']
    except KeyError:
        comments_list = []
    return comments_list


# convert responses to a list of parsed posts
def post_list_from_response(response, headers):
    post_list_batch = []
    i = 0

    # loop through each post pulled from response and append to a list
    for post in response.json()['data']['children']:
        post_data = {
            '_id': post['data']['id'],
            'kind': post['kind'],
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'author': post['data']['author'],
            'author_fullname': post['data']['author_fullname'],
            'selftext': post['data']['selftext'],
            'num_comments': post['data']['num_comments'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score']
        }

        post_list_batch.append(post_data)
        i += 1
        print(f'single post processing {i}/100')
        # don't overload the servers with requests
        sleep(1)
        # get and persist the comments for the current post
        fetch_comments_from_post(post['data']['id'], headers)

    return post_list_batch
