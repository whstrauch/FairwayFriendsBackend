import requests

def request(path, method="POST", body={}):
    resp = requests.request(
        method,
        f"http://host.minikube.internal:5005/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp