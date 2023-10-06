import requests

def request(path, method="POST", body={}):


    resp = requests.request(
        method,
        f"http://10.0.0.221:5006/{path}",
        headers={'content-type': 'application/json'},
        json=body
    )
    return resp