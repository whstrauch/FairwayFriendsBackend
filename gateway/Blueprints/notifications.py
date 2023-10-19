import json
from flask import request, Blueprint
from authsvc import validate
from notisvc import notirequest
from postsvc import post_request
from usersvc import user_request

notifications = Blueprint("notifications", __name__)

@notifications.get("/notifications/<int:id>")
def get_notis(id):

    # valid, err = validate.token(request)
    # if err:
    #     return err

    resp = notirequest.request(f"{id}", "GET")
    
    final_result = []
    if resp.ok:
        result = resp.json()
        for noti in result["main_notis"]:
            # Fetch like or comment
            print("subject")
            subject = post_request.request(f'/{noti["n_type"]}/{noti["source_id"]}', "GET")
            if subject.ok:
                subject_json = subject.json()
            else:
                continue
            # Fetch user info
            print("user", subject_json)
            user = user_request.request(f"/get/{subject_json['user_id']}", "GET")
            if user.ok:
                user_json = user.json()
            else:
                return "error-user", 400
            # Fetch post pic
            print("post", user_json)
            post = post_request.request(f"/get/{subject_json['post_id']}", "GET")
            if post.ok:
                post_json = post.json()
            else:
                return "error-post", 400
            final_result.append({"user": user_json, "post": {"id": post_json["id"], "media": post_json["media"]}, "subject": subject_json, "n_type": noti["n_type"]})
        result["main_notis"] = final_result
        return result, 200
    else:
        return "error-main", 400
