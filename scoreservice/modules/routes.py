from flask import Blueprint, request, Flask
import gridfs
from flask_pymongo import PyMongo
from bson import json_util, ObjectId

mongo = PyMongo()
score = Blueprint("score", __name__)

"""
Methods to add:
    Update score,
    Get all scores for user,
"""

@score.post('/create')
def add_score():
    data = request.get_json(force=True)

    result = mongo.db.scores.insert_one(
        data
    )
    if result:
        return {"id": str(result.inserted_id)}, 201
    return {"text": "Failure"}, 400

@score.get('/score/post/<string:post_id>')
def get_score(post_id):
    score = mongo.db.scores.find_one({"post_id": post_id})
    if score:
        oid = str(score["_id"])
        score.pop("_id")
        return {"id": oid, **score}, 200
    return {"text": "Failure"}, 400

@score.get('/score/<string:id>')
def get_score_id(id):
    id = ObjectId(id)
    score = mongo.db.scores.find_one({"_id": id})
    if score:
        oid = str(score["_id"])
        score.pop("_id")
        return {"id": oid, **score}, 200
    return {"text": "Failure"}, 400

@score.get('/score/user/<string:id>')
def get_user_scores(id):
    scores = mongo.db.scores.find({"user_id": id})
    if scores:
        return_scores = []
        for score in scores:
            id = str(score.pop("_id"))
            return_scores.append({"id": id, **score})
        return return_scores, 200
    return {"text": "Failure"}, 400