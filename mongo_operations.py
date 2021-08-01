#!/usr/bin/env python3
import pymongo

mongo = pymongo.MongoClient(
    "localhost",
    27017,
    username="user",
    password="pw")

db = mongo.db


def persist_post(post_data):
    db.posts.insert_one(post_data)


def persist_post_list(post_list):
    db.posts.insert_many(post_list)


def persist_comment(comment_data, post_id):
    db[f'{post_id}_comments'].insert_one(comment_data)
