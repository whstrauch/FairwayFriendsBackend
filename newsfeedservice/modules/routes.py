from flask import Blueprint, request, Flask
import gridfs
from flask_pymongo import PyMongo
from bson import json_util, ObjectId

mongo = PyMongo()
newsfeed = Blueprint("newsfeed", __name__)

"""
Methods to add:
    Update score,
    Get all scores for user,
"""

@newsfeed.get('/newsfeed/<int:id>')
def get_newsfeed(id):
    """
    Gets newsfeed for specified user.
    """
    nfeed = mongo.db.newsfeed.find_one({"_id": id})
    return nfeed["newsfeed_list"], 200