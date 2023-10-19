import requests

def request(path, meth="POST", body={}):
    resp = requests.request(
        meth,
        f"http://10.18.196.187:5008/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp