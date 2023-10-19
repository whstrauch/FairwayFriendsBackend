import requests

def request(path, meth="POST", body={}):
    resp = requests.request(
        meth,
        f"http://host.minikube.internal:5008/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp