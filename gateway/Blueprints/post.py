import json
import time
from flask import request, Blueprint
import requests, os, gridfs
from authsvc import validate, auth_request
from postsvc import post_request
import pika
import uuid
from pymongo import MongoClient
from bson import ObjectId


mongo = MongoClient('mongodb://localhost:27017/')
db = mongo.fairwayfriends
fs = gridfs.GridFS(db)



post_routes = Blueprint("post", __name__)

## can add in global connection here to be used for sending messages. ie publisher
# publishing_connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq')) #rabbitmq is name of container with rabbitmq instance
# channel = publishing_connection.channel()

@post_routes.get('/post/<int:id>')
def get_post(id):
    """
    Gets post to be displayed, gets metadata
    """

    # Auth
    valid, err = validate.token(request)
    if err:
        return err

    post, status = post_request.request(f'get/{id}')
    if status == 200:
        return post, 200
    else:
        return "Failure", 400

@post_routes.get('/post/user/<int:id>')
def get_user_post(id):
    """
    Gets posts of user to be displayed, gets metadata and images
    """

    # Auth
    valid, err = validate.token(request)
    if err:
        return err

    post = post_request.request(f'get/user/{id}', "GET")
    if post.status_code == 200:
        return post.json(), 200
    else:
        return "Failure", 400

@post_routes.get('/post/media/<string:path>')
def get_image(path):
    file = fs.find_one({"_id": ObjectId(path)})
    data = file.read()
    return data, 200

    
    

@post_routes.post('/post')
def create_post():
    """
    Creates a post, data that must be passed -> media list (photos/videos)
    Title, Caption, User ID, tagged users, course, score data, round data.
    """

    # Auth
    valid, err = validate.token(request)
    if err:
        return err

    # Retrieve data
    

    

    
    # universal_id = uuid.uuid4()

    #Save Images, will update to azure blob whenever deployed
    # for media in data["media"]:
    #     random_path = str(uuid.uuid4())
    #     pathname = f'/Users/willstrauch/Desktop/ImageTesting/{random_path}'

    #     # save images to s3, get id
    #     with open(pathname, 'wb') as file:
    #         file.write(media["uri"])
        
    #     image_uris.append(pathname)
    # Metadata to be saved in post table
    image_uris = []
    sizes = request.form["size[]"].split(",")
    max_ratio = 1
    for i, file in enumerate(request.files.getlist("uploadFiles[]")):
        fid = fs.put(file.stream)
        image_uris.append({"path": str(fid), "width": sizes[i*2], "height": sizes[(i*2)+1]})
        ratio = int(sizes[(i*2) + 1]) / int(sizes[i*2])
        max_ratio = min(1.4, max(max_ratio, ratio))

    post_metadata = {
        "title": request.form.get('title', ''),
        'caption': request.form.get('description', ''),
        "user_id": request.form["user"],
        "course_id": request.form["course_id"],
        "course_name": request.form["course_name"],
        "ratio": max_ratio
    }
    print("Saving metadata...", post_metadata)

    try:
        post = post_request.request('create', "POST", post_metadata)
        if post.status_code != 201:
            return "Failed", 400
    except Exception as e:
        return e, 400

    post_id = post.json()["id"]
    print("Metadata uploaded...", post_id)

    score_data = request.form["score"]

    print("Score data uploaded...")
    # Save score to score service

    

    tags = {
        "post_id": post_id,
        "tagged": request.form.getlist('taggedFriends[]')
    }

    print("tags", tags)

    try:
        message = post_request.request('tag/add', "POST",tags)
        if message.status_code != 201:
            return message, message.status_code
    except Exception as e:
        return e, 400

    print("Tags uploaded...")


    media = {
        "post_id": post_id,
        "media": image_uris
    }

    try:
        message = post_request.request('media/add', "POST", media)
        if message.status_code != 201:
            return "Failure", 400
    except Exception as e:
        return e, 400


    # Tells newsfeed of new post by user_id
    message = {
        "post_id": post_id,
        "user_id": request.form["user"]
    } ## -> Contains uris of media to uploaded, and uuid (maybe)
    
    # channel.basic_publish('', 'newsfeed', message)

    return "Success", 200

@post_routes.delete('/post/delete')
def delete_post():
    """
    Takes post id, user id -> deletes post from db
    """
    ## MAKE SURE TO ADD IN DELETING IMAGES FROM IMAGE STORAGE

    valid, err = validate.token(request)
    if err:
        return err


    try: 
        data = request.get_json(force=True)
        body = {
            'user_id': data.get('user_id'),
            'post_id': data.get('post_id')
        }
        message = post_request.request('delete', body, "DELETE")
        return message.text, message.status_code
    except Exception as e:
        return e, 400

    

@post_routes.post('/post/edit')
def edit_post():
    """
    Edits a post, data that must be passed -> media list (photos/videos)
    Title, Description, User ID, tagged users, course, score data, round data.
    """
    # First send media to media service, media service attempts to add images, if 
    # successful sends to post service to add metadata, with ids of image locations?, 
    # if that is successful sends message to newsfeed service to update newsfeed for
    # all followers of user that j submitted post. All same idea

    valid, err = validate.token(request)
    if err:
        return err

    pass


@post_routes.post('/post/like')
def like_post():
    """
    Takes in a post id, user id -> sends to post service to add like to post
    """

    valid, err = validate.token(request)
    if err:
        return err
    data = request.get_json(force=True)

    message = post_request.request('like/add', "POST", data)
    return message.text, message.status_code

    ## Send message to notification service to notify liked account

@post_routes.get('/like/<int:post_id>/<int:user_id>')
def is_liked(post_id, user_id):
    """
    Checks if user has liked post.
    """
    message = post_request.request(f'like/{post_id}/{user_id}', "GET")
    return message.json(), message.status_code
  

@post_routes.delete('/post/like/delete')
def delete_like_post():
    """
    Takes in post id, user id -> deletes like from table
    """

    valid, err = validate.token(request)
    if err:
        return err

    data = request.get_json(force=True)

    message = post_request.request('like/remove', "DELETE", data)
    return message.text, message.status_code

@post_routes.post('/post/comment')
def comment_post():
    """
    Takes in a post id, user id, text -> sends to post service to add comment to post
    """

    valid, err = validate.token(request)
    if err:
        return err

    data = request.get_json(force=True)

    message = post_request.request('comment/add', "POST", data)
    return message.text, message.status_code

@post_routes.get('/post/comments/<int:id>')
def get_comments(id):
    """
    Get list of comments from given post id -> text, and user
    """
    valid, err = validate.token(request)
    if err:
        return err

    data = request.get_json(force=True)

    message = post_request.request('')

    pass

    

@post_routes.delete('/post/comment/delete')
def delete_comment_post():
    """
    Takes in post id, user id -> deletes comment from table
    """
    valid, err = validate.token(request)
    if err:
        return err

    pass

