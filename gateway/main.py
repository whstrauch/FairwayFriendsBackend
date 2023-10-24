from flask import Flask
from azure.storage.blob import BlobServiceClient
import os, logging
from waitress import serve


connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def create_blob_root_container(blob_service_client: BlobServiceClient):
    container_client = blob_service_client.get_container_client(container="$root")
    # Create the root container if it doesn't already exist
    if not container_client.exists():
        container_client.create_container()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config["DEBUG"] = False
    # app.config["API_URL"] = "localhost"
    from Blueprints.user import user_routes
    from Blueprints.post import post_routes
    from Blueprints.course import course_routes
    from Blueprints.newsfeed import newsfeed
    from Blueprints.notifications import notifications
    app.register_blueprint(user_routes)
    app.register_blueprint(post_routes)
    app.register_blueprint(course_routes)
    app.register_blueprint(newsfeed)
    app.register_blueprint(notifications)
    create_blob_root_container(blob_service_client)
    ## Create consumer here so new connection and channel
    ## Dont pass connection
    
    
    return app

if __name__ == "__main__":
    print("creating app...")
    app = create_app()
    print("app created, starting server...")
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(app, host='localhost', port=5000)
    print('server closed')