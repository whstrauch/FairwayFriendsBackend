from flask import Flask
from flask_pymongo import PyMongo
from mongoflask import MongoJSONEncoder, ObjectIdConverter
import pika, sys, os, threading, json, time, requests

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.json_encoder = MongoJSONEncoder
    app.config["MONGO_URI"] = "mongodb://localhost:27017/fairwayfriends"
    
    from routes import mongo, newsfeed
    app.register_blueprint(newsfeed)
    
    
    with app.app_context():
        mongo.init_app(app)
    
    return app

def update_newsfeeds(channel, method, properties, body):
    """
    Callback when message is received, message contains post id and 
    user id to update all newsfeeds for users that follow the poster.
    """
    from routes import mongo
    message = json.loads(body)
    user_id = message["user_id"]
    post_id = message["post_id"]
    #fetch user followers from user service

    resp = requests.request(
        "GET",
        f"http://10.0.0.221:5002/followers/get/{user_id}/{user_id}",
        headers={'content-type': 'application/json'}
    )
    
    followers = resp.json()
    # users=[{"user_id": 3, "post_id": 2}]

    #from list of followers add post id to their newsfeed
    for user in followers:
        print(user)
        mongo.db.newsfeed.find_one_and_update({"_id": user.get("user_id")}, 
            { "$addToSet": {"newsfeed_list": post_id}}
        ,
        upsert=True)
    
    

    print("MESSAGE RECEIVED", message)
    if channel:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def queue_consume(channel):
    #rabbitmq connection
    channel.start_consuming()

def main():

    app = create_app()
    
    # queue_thread = threading.Thread(target=queue_consume)
    # queue_thread.start()
    app_thread = threading.Thread(target=app.run, kwargs={"host":'10.0.0.221',"port": 5006, "debug": False})
    app_thread.start()
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672, heartbeat=60)
    )
    channel = connection.channel()
    channel.queue_declare(queue="newsfeed")
    channel.basic_consume(queue="newsfeed", on_message_callback=update_newsfeeds)
    print("Queue consuming started.")
    
    queue_thread = threading.Thread(target=queue_consume, args=(channel,))
    queue_thread.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)