from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import sys, os, threading, pika, json, requests

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://willstrauch:Soccer99@{os.environ.get('POSTGRESQL_HOST')}:5432/fairwayfriends"
    app.config["DEBUG"] = True
    from models import db
    from routes import notifications
    app.register_blueprint(notifications)
    
    with app.app_context():
        db.init_app(app)
        # db.drop_all()
        db.create_all()

    
    return app

def callback(channel, method, properties, body):
    """
    Callback when message is received, message contains post id and 
    user id to update all newsfeeds for users that follow the poster.
    """
    
    
    # Post notification to table
    resp = requests.request(
        "POST",
        f"http://host.minikube.internal:5007/",
        headers={'content-type': 'application/json'},
        data=body
    )

    if channel:
        channel.basic_ack(delivery_tag=method.delivery_tag)



def queue_consume(channel):
    #rabbitmq connection
    channel.start_consuming()

def main():

    app = create_app()
    
    # queue_thread = threading.Thread(target=queue_consume)
    # queue_thread.start()
    app_thread = threading.Thread(target=app.run, kwargs={"host":'0.0.0.0',"port": 5007, "debug": False})
    app_thread.start()
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="host.minikube.internal", port=5672, heartbeat=60)
    )
    channel = connection.channel()
    channel.queue_declare(queue="notifications")
    channel.basic_consume(queue="notifications", on_message_callback=callback)
    print("Queue consuming started.")
    
    queue_thread = threading.Thread(target=queue_consume, args=(channel,))
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
