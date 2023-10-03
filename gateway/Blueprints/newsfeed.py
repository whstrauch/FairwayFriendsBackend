import json
from flask import request, Blueprint
import requests, os
from authsvc import validate
from newsfeedsvc import newsfeed_request
from postsvc import post_request

newsfeed = Blueprint("newsfeed", __name__)


@newsfeed.get('/newsfeed/<int:id>')
def get_newsfeed(id):
    """
    Takes in user_id and return list of post ids for up to date newsfeed.
    Should add pagination
    """
    # valid, err = validate.token(request)
    # if err:
    #     return err

    resp = newsfeed_request.request(f"newsfeed/{id}", "GET")

    if resp.ok:
        post_ids = resp.json()
        post = post_request.request(f'getlist', "POST", {"ids": post_ids})
        if post.status_code == 200:
            return post.json(), 200
        else:
            return "error", 400
    else:
        return "error", 400