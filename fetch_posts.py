#!/usr/bin/env python3
import requests
from time import sleep
import mongo_operations
import fetch_operations

with open('api_key.txt', 'r') as key_file:
    CLIENT_ID, SECRET_KEY = key_file.read().strip('\n').split('\n')

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

with open('secret.txt', 'r') as pw_file:
    user, pw = pw_file.read().strip('\n').split('\n')

user_data = {
    'grant_type': 'password',
    'username': user,
    'password': pw
}

headers = {'User-Agent': 'HwAPI/0.0.1'}

# Important: This access Token will expire after 2 hours (or 1?), a new one has to be requested (permanent?)
# https://github.com/reddit-archive/reddit/wiki/OAuth2

res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=user_data, headers=headers)
TOKEN = res.json()['access_token']
headers['Authorization'] = f'bearer {TOKEN}'

# connect to running mongodb instance
mongo_client = mongo_operations.mongo
db = mongo_client.db

# Important: The API has a limit of requests per minute, monitor the usage.
# https://github.com/reddit-archive/reddit/wiki/API
params = {'limit': 100}
N_POST_BATCHES = 5

# fetch N * 100 posts
for i in range(N_POST_BATCHES):
    res = requests.get("https://oauth.reddit.com/r/sanfrancisco/new",
                       headers=headers,
                       params=params)

    post_list = fetch_operations.post_list_from_response(res)
    # take the final row (oldest entry)
    last_row = post_list[:-1][0]
    # create fullname id, like t3_000000
    fullname = last_row['kind'] + '_' + last_row['id']
    # add/update fullname in params, to
    params['after'] = fullname

    # persist list of posts in mongo, using insert_many()
    mongo_operations.persist_post_list(post_list)
    # don't overload the servers with requests
    sleep(1)
