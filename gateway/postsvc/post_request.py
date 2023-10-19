import requests

def request(path, method="POST", body={}):


    resp = requests.request(
        method,
        f"http://host.minikube.internal:5003/",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp