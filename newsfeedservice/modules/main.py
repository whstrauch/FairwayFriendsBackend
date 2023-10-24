from flask import Flask
from flask_pymongo import PyMongo
from mongoflask import MongoJSONEncoder, ObjectIdConverter
import sys, os, threading, json, logging, requests
from azure.servicebus import ServiceBusClient
from waitress import serve

CONNECTION_STRING = os.environ.get("MQ_CONNECTION_STRING")
QUEUE_NAME = "newsfeed"


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.json_encoder = MongoJSONEncoder
    app.config["MONGO_URI"] = os.environ.get('MONGODB_CONNECTION_STRING')
    
    from routes import mongo, newsfeed
    app.register_blueprint(newsfeed)
    
    
    with app.app_context():
        mongo.init_app(app)
    
    return app

def update_newsfeeds(body):
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
        f"http://userservice:5002/followers/get/{user_id}/0",
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

def receive_messages():
    print("receiving messages...")
    with ServiceBusClient.from_connection_string(CONNECTION_STRING) as client:
    # max_wait_time specifies how long the receiver should wait with no incoming messages before stopping receipt.
    # Default is None; to receive forever.
        with client.get_queue_receiver(QUEUE_NAME) as receiver:
            for msg in receiver:  # ServiceBusReceiver instance is a generator.
                update_newsfeeds(msg)

def main():
    print('creating app...')
    app = create_app()
    print('app created, configuring logging...')
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    app_thread = threading.Thread(target=serve, args={app}, kwargs={"host":'localhost',"port": 5006})
    app_thread.start()
    #Might have to be adjusted with messaging bus.
    
    queue_thread = threading.Thread(target=receive_messages)
    queue_thread.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)