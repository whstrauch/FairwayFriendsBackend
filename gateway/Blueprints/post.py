import json
import time
from flask import request, Blueprint
import requests, os, gridfs
from authsvc import validate
from postsvc import post_request
from scoresvc import score_request
import pika
from pymongo import MongoClient
from bson import ObjectId


mongo = MongoClient('mongodb://host.minikube.internal:27017/')
db = mongo.fairwayfriends
fs = gridfs.GridFS(db)



post_routes = Blueprint("post", __name__)

## can add in global connection here to be used for sending messages. ie publisher


@post_routes.get('/testrabbitmq')
def test_rabbitmq():
    publishing_connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="host.minikube.internal", port=5672, heartbeat=60)
    )
    channel = publishing_connection.channel()
    channel.basic_publish(
                            exchange= '', 
                            routing_key='newsfeed',
                            body=json.dumps({"user_id": 1, "post_id": 4}),
                            properties=pika.BasicProperties(content_type='text/plain',
                                                          delivery_mode=pika.DeliveryMode.Persistent))
    return "Publisshed", 200

@post_routes.get('/post/<int:id>')
def get_post(id):
    """
    Gets post to be displayed, gets metadata
    """

    # Auth
    valid, err = validate.token(request)
    if err:
        return err

    post = post_request.request(f'get/{id}')
    if post.status_code == 200:
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
    Should add more graceful error handling.
    """

    # Auth
    valid, err = validate.token(request)
    if err:
        return err

    # Metadata to be saved in post table
    image_uris = []
    sizes = request.form["size[]"].split(",")
    max_ratio = 1

    #Calculate aspect ratio for media to set for post display
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
        "ratio": max_ratio,
        "score": request.form["score_string"]
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
    score_data = json.loads(score_data)
    upload_data = {
        "post_id": post_id,
        "score": score_data["userScore"],
        "holes": score_data["holes"]
    }
    # Save score to score service
    try:
        test = score_request.request("create", "POST", upload_data)
        if not test.ok:
            return test.text, test.status_code
    except Exception as e:
        return e, 400

    print("Score data uploaded...")

    tags = {
        "post_id": post_id,
        "tagged": request.form.getlist('taggedFriends[]')
    }

    print("tags", tags)

    if len(tags) != 0:
        try:
            message = post_request.request('tag/add', "POST",tags)
            if message.status_code != 201:
                return message.text, message.status_code
        except Exception as e:
            return e, 400

    print("Tags uploaded...")


    if len(image_uris) != 0:
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
    news_message = {
        "post_id": post_id,
        "user_id": request.form["user"]
    } ## -> Contains uris of media to uploaded, and uuid (maybe)



    ##Creates rabbitmq connection and channel.
    publishing_connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="host.minikube.internal", port=5672, heartbeat=60)
    )
    channel = publishing_connection.channel()
    
    channel.basic_publish(
                            exchange= '', 
                            routing_key='newsfeed',
                            body=json.dumps(news_message),
                            properties=pika.BasicProperties(content_type='text/plain',
                                                          delivery_mode=pika.DeliveryMode.Persistent)
    )


    return "Success", 200

@post_routes.delete('/post/delete')
def delete_post():
    """
    Takes post id, user id -> deletes post from db
    """
    ## MAKE SURE TO ADD IN DELETING IMAGES FROM IMAGE STORAGE
    ## Also message to newsfeed service to remove post?

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

    if message.ok:
        post_id = data["post_id"]
        count_message = post_request.request(f'like-count/inc/{post_id}', "PUT")
        return count_message.text, count_message.status_code

    return message.text, message.status_code

    ## Send message to notification service to notify liked account

@post_routes.get('/like/<int:post_id>/<int:user_id>')
def is_liked(post_id, user_id):
    """
    Checks if user has liked post.
    """
    message = post_request.request(f'like/{post_id}/{user_id}', "GET")
    return message.json(), message.status_code

@post_routes.get('/likes/<int:post_id>')
def get_likes(post_id):
    """
    Get likes of post, paginated
    """
    message = post_request.request(f'likes/{post_id}', "GET")
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
    if message.ok:
        post_id = data["post_id"]
        count_message = post_request.request(f'like-count/dec/{post_id}', "PUT")
        return count_message.text, count_message.status_code
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

    message = post_request.request(f'comments/{id}', "GET")

    return message.text, message.status_code

    

@post_routes.delete('/post/comment/delete')
def delete_comment_post():
    """
    Takes in post id, user id -> deletes comment from table
    """
    valid, err = validate.token(request)
    if err:
        return err

    pass


@post_routes.get("/score/get/<int:id>")
def get_score(id):
    """
    Gets score from given post id.
    """

    res = score_request.request(f"score/post/{id}", "GET")

    return res.text, res.status_code


