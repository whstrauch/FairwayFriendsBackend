from flask import Flask
from flask_pymongo import PyMongo
import logging, os
from waitress import serve
from mongoflask import MongoJSONEncoder, ObjectIdConverter


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.json_encoder = MongoJSONEncoder
    app.config["MONGO_URI"] = os.environ.get('MONGODB_CONNECTION_STRING')
    
    from routes import score, mongo
    app.register_blueprint(score)
    
    
    with app.app_context():
        mongo.init_app(app)
    
    return app

if __name__ == "__main__":
    print('creating app...')
    app = create_app()
    print('app created, config logger')
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    print('starting server...')
    serve(app, host='localhost', port=5008)
    print('server closed...')