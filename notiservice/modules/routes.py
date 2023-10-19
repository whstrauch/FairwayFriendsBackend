from flask import request, Blueprint
from models import db, NotificationsModel
import datetime

notifications = Blueprint("notifications", __name__)

"""
Routes needed:
    List of notifications for user.
    Post notification
    Delete notification
"""

@notifications.get("/")
def test():
    return "Text", 200

@notifications.post("/")
def new_notification():
    print("entered")
    data = request.get_json(force=True)
    print("post_data", data)
    # try:
    notification = NotificationsModel(
        source_id = data["source_id"],
        n_type = data["n_type"],
        user_id = data["user_id"],
        timestamp = datetime.datetime.utcnow()
    )
    db.session.add(notification)
    db.session.commit()
    return {"info": "Success"}, 201
    # except Exception as e:
        # return {"info": e}, 400

@notifications.get("/<int:id>")
def get_user_notis(id):
    """
    Get top 20 notifications? for a given user, pagination. Should get all
    follow requests no matter what.
    """
    stmt = db.select(NotificationsModel).where(NotificationsModel.user_id == id)
    result = db.session.execute(stmt)
    frs = []
    main_notis = []
    for item in result.scalars().all():
        if item.n_type == "follow_request":
            frs.append(item.toJSON())
        else:
            main_notis.append(item.toJSON())

    return {"follow_requests": frs, "main_notis": main_notis}, 200