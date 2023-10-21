from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import pika, os
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient

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
    app.config["DEBUG"] = True
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
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)