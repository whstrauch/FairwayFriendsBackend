import requests

def request(path, body):
    resp = requests.post(
        f"http://127.0.0.1:5001/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp