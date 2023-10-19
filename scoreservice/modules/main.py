from flask import Flask
from flask_pymongo import PyMongo
from mongoflask import MongoJSONEncoder, ObjectIdConverter


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.json_encoder = MongoJSONEncoder
    app.config["MONGO_URI"] = "mongodb://localhost:27017/fairwayfriends"
    
    
    from routes import score, mongo
    app.register_blueprint(score)
    
    
    with app.app_context():
        mongo.init_app(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5008, host='10.18.196.187', debug=True)