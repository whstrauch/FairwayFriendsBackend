import requests

def request(path, meth="POST", body={}):
    resp = requests.request(
        meth,
        f"http://10.0.0.221:5002/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp