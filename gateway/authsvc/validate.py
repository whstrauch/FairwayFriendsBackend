import requests

def token(request):
    if not "Authorization" in request.headers:
        return None, ("Missing credentials", 401)
    
    token = request.headers["Authorization"]
    if not token:
        return None, ("Missing credentials", 401)

    resp = requests.post(
        f"http://authservice:5001/verify",
        headers={"Authorization" : token}
    )
    if resp.status_code == 200:
        return resp.json(), None
    else:
        return None, (resp.text, resp.status_code)