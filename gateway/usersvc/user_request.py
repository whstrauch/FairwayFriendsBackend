import requests

def request(path, meth="POST", body={}):
    resp = requests.request(
        meth,
        f"http://127.0.0.1:5002/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp