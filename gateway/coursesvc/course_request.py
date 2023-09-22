import requests

def request(path, method="POST", body={}):
    resp = requests.request(
        method,
        f"http://127.0.0.1:5005/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp