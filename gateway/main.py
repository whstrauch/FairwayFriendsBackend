from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pika

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["DEBUG"] = True
    from Blueprints.user import user_routes
    from Blueprints.post import post_routes
    from Blueprints.course import course_routes
    app.register_blueprint(user_routes)
    app.register_blueprint(post_routes)
    app.register_blueprint(course_routes)
    ## Create consumer here so new connection and channel
    ## Dont pass connection
    
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)