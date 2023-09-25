from flask import request, Blueprint
import requests, os, gridfs, json, uuid
from authsvc import validate, auth_request
from usersvc import user_request
from pymongo import MongoClient
from bson import ObjectId

mongo = MongoClient('mongodb://localhost:27017/')
db = mongo.fairwayfriends
fs = gridfs.GridFS(db)


user_routes = Blueprint("user", __name__)

@user_routes.post('/login')
def login():
    """
    Performs login from username/email, returns jwt token for future authentication.
    Unprotected.
    """
    resp = auth_request.request('login', request.json)
    if resp.status_code == 200:
        return resp.json(), 200
    else:
        return resp.text, resp.status_code


@user_routes.post('/create')
def create_user():
    """
    Creates auth service user in database, if successful returns user id and token.
    Unprotected.
    """

    auth_resp = auth_request.request('create', request.json)

    if auth_resp.status_code == 201:
        ## Create base user in user info table, including id, update to user service address
        json, code = login()

        return json, 201
    else:
        return auth_resp.text, auth_resp.status_code

@user_routes.get('/user/<int:id>')
def get_user(id):
    """
    Gets user from id
    Protected.
    """
    valid, err = validate.token(request)
    if err:
        return err

    resp = user_request.request(f'get/{id}', "GET")

    if resp.status_code == 201:
        return resp, 201
    else:
        return resp.text, resp.status_code


@user_routes.post('/user/create')
def create_user_info():
    """
    Create user for user info table, should already have id from login/create account phase.
    Protected.
    """
    valid, err = validate.token(request)
    if err:
        return err

    print("gateway")
    resp = user_request.request('create', "POST", request.json)

    if resp.status_code == 201:
        return {"text": "Success"}, 201
    else:
        return resp.text, resp.status_code

@user_routes.route('/user/profile_pic', defaults={"path": "post"}, methods=["GET", "POST"])
@user_routes.route('/user/profile_pic/<string:path>', methods=["GET", "POST"])
def user_prof_pic(path):
    """
    Add or update profile pic.
    """
    

    if request.method == "GET":
        file = fs.find_one({"_id": ObjectId(path)})
        data = file.read()
        return data, 200
    valid, err = validate.token(request)
    if err:
        return err
    file = request.files["profile_pic"]
    fid = fs.put(file.stream, user_id=request.form["user_id"])
    data = {
        "user_id": request.form["user_id"],
        "path": str(fid)
    }
    resp = user_request.request('profile-pic', "POST", data)
    return resp.text, resp.status_code



@user_routes.put('/user/update/<id>')
def update_user_info(id):
    """
        Takes user id and updates user info, can be used during account creation.
        Protected.
    """
    valid, err = validate.token(request)
    if err:
        return err
    
    data = request.get_json(force=True)
    data["user_id"] = id

    resp = user_request.request('edit', "PUT", data)

    if resp.status_code == 201:
        return {"text": "Success"}, 201
    else:
        return resp.text, resp.status_code

    


@user_routes.get('/user/search/<string:query>')
def search_users(query):
    """
    Search for users based on query. Return list of users (add pagination?)
    Protected.
    """
    valid, err = validate.token(request)
    if err:
        return err

    results = user_request.request(f'search?{query}', "GET")

    if results.status_code == 200:
        return results.json(), 200
    else:
        return "Failure", 400

    

@user_routes.get('/user/followers/<int:id>/<int:main_id>')
def get_followers(id, main_id):
    valid, err = validate.token(request)
    if err:
        return err

    resp = user_request.request(f'followers/get/{id}/{main_id}', "GET")

    if resp.status_code == 200:
        return resp.text, 200
    else:
        return resp.text, resp.status_code

@user_routes.get('/user/following/<int:id>/<int:main_id>')
def get_following(id, main_id):
    valid, err = validate.token(request)
    if err:
        return err

    resp = user_request.request(f'following/get/{id}/{main_id}', "GET")

    if resp.status_code == 200:
        return resp.text, 200
    else:
        return resp.text, resp.status_code

@user_routes.delete('/user/unfollow')
def unfollow():
    valid, err = validate.token(request)
    if err:
        return err

    resp = user_request.request(f'unfollow', "DELETE", request.get_json(force=True))

    if resp.status_code == 200:
        return resp.text, 200
    else:
        return resp.text, resp.status_code

@user_routes.post('/user/follow')
def follow_request():
    valid, err = validate.token(request)
    if err:
        return err

    resp = user_request.request('follow', "POST", request.get_json(force=True))

    if resp.status_code == 200:
        return resp.text, 200
    else:
        return resp.text, resp.status_code

@user_routes.post('/user/users')
def get_user_list():
    """
    Get list of users, for comments and likes lists.
    Should add pagination
    """
    valid, err = validate.token(request)
    if err:
        return err
    
    resp = user_request.request('userlist', "POST", request.get_json(force=True))

    return resp.json(), resp.status_code




    
    

