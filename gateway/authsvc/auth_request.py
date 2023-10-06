import requests
import os

def request(path, body):
    resp = requests.post(
        f"http://10.0.0.221:5001/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp
