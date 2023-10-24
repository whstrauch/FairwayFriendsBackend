from flask import Flask
import os, logging
from waitress import serve

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.environ.get('POSTGRESQL_USER')}:{os.environ.get('POSTGRESQL_PASSWORD')}@{os.environ.get('POSTGRESQL_HOST')}:5432/fairwayfriends"
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get('JWT_SECRET')
    app.config["JWT_ACCESS_LIFESPAN"] = {"days": 1}
    app.config["JWT_REFRESH_LIFESPAN"] = {"days": 1}
    from models import db, guard, AuthModel
    from routes import auth
    app.register_blueprint(auth)
    
    with app.app_context():
        guard.init_app(app, AuthModel)
        db.init_app(app)
        # db.drop_all()
        db.create_all()

    
    return app

if __name__ == "__main__":
    print("Starting auth service...")
    app = create_app()
    print("app created, starting server...")
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host='localhost', port=5001)
    print('server closed')