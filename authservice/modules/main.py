from flask import Flask
import os

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{os.environ.get('POSTGRESQL_USER')}:{os.environ.get('POSTGRESQL_PASSWORD')}@{os.environ.get('POSTGRESQL_HOST')}:5432/fairwayfriends"
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("JWT_SECRET")
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
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)