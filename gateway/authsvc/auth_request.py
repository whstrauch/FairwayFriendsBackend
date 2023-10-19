import requests
import os

def request(path, body):
    resp = requests.post(
        f"http://10.18.196.187:5001/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp
