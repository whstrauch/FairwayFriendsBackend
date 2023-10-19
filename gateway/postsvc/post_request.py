import requests

def request(path, method="POST", body={}):


    resp = requests.request(
        method,
        f"http://10.18.196.187:5003/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp