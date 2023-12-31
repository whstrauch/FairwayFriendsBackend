from flask import Flask
import sys, os, threading, logging, requests
from waitress import serve

from azure.servicebus import ServiceBusClient

CONNECTION_STRING = os.environ.get('MQ_CONNECTION_STRING')
QUEUE_NAME = "notifications"

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.environ.get('POSTGRESQL_USER')}:{os.environ.get('POSTGRESQL_PASSWORD')}@{os.environ.get('POSTGRESQL_HOST')}:5432/fairwayfriends"
    app.config["DEBUG"] = False
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
    print('receiving messages...')
    with ServiceBusClient.from_connection_string(CONNECTION_STRING) as client:
    # max_wait_time specifies how long the receiver should wait with no incoming messages before stopping receipt.
    # Default is None; to receive forever.
        with client.get_queue_receiver(QUEUE_NAME) as receiver:
            for msg in receiver:  # ServiceBusReceiver instance is a generator.
                callback(msg)

def main():
    print('creating app...')
    app = create_app()
    
    # queue_thread = threading.Thread(target=queue_consume)
    # queue_thread.start()
    print('app created, configuring logging...')
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    app_thread = threading.Thread(target=serve, args={app}, kwargs={"host":'localhost',"port": 5007})
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
