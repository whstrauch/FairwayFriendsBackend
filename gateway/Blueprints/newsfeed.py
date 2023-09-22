import json
from flask import request, Blueprint
import requests, os
from authsvc import validate, auth_request

newsfeed = Blueprint("newsfeed", __name__)


@newsfeed.get('/newsfeed')
def get_newsfeed():
    """
    Takes in user_id and return list of post ids for up to date newsfeed.
    """

    pass