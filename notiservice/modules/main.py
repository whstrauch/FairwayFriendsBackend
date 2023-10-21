from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import sys, os, threading, pika, json, requests

from azure.servicebus import ServiceBusClient

CONNECTION_STRING = "Endpoint=sb://fairwayfriends.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=QorxUPJlWEA+L1vk9ELulua0Ain7BiBHu+ASbFKYJ1M="
QUEUE_NAME = "notifications"

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.environ.get('POSTGRESQL_USER')}:{os.environ.get('POSTGRESQL_PASSWORD')}@{os.environ.get('POSTGRESQL_HOST')}:5432/fairwayfriends"
    app.config["DEBUG"] = True
    from models import db
    from routes import notifications
    app.register_blueprint(notifications)
    
    with app.app_context():
        db.init_app(app)
        # db.drop_all()
        db.create_all()

    
    return app

def callback(body):
    """
    Callback when message is received, message contains post id and 
    user id to update all newsfeeds for users that follow the poster.
    """
    
    
    # Post notification to table
    resp = requests.request(
        "POST",
        f"http://notiservice:5007/",
        headers={'content-type': 'application/json'},
        data=body
    )



def queue_consume():
    #azuremq connection
    with ServiceBusClient.from_connection_string(CONNECTION_STRING) as client:
    # max_wait_time specifies how long the receiver should wait with no incoming messages before stopping receipt.
    # Default is None; to receive forever.
        with client.get_queue_receiver(QUEUE_NAME) as receiver:
            for msg in receiver:  # ServiceBusReceiver instance is a generator.
                callback(msg)

def main():

    app = create_app()
    
    # queue_thread = threading.Thread(target=queue_consume)
    # queue_thread.start()
    app_thread = threading.Thread(target=app.run, kwargs={"host":'0.0.0.0',"port": 5007, "debug": False})
    app_thread.start()
    #Adjust with azure messaging bus
    
    
    queue_thread = threading.Thread(target=queue_consume)
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
