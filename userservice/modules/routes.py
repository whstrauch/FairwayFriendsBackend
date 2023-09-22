from datetime import datetime, timezone
from os import abort
from flask import jsonify, request, Blueprint
from models import db, UserModel, SocialRelationships
from sqlalchemy import func, or_, text

user = Blueprint("user", __name__)

"""
Most of these can be synchronous.
Routes needed:
    Get user
    Create user
    Edit user
    Delete user
    Handle social relationships:
        Follow request -> send message to notification service to notify of new follower
        Unfollow/Delete request
        Accept request
"""

@user.get("/get/<id>")
def get_user(id):
    """
    Gets a user based on given id.
    """
    if id.isnumeric():
        curr_user = db.get_or_404(UserModel, int(id))
        if not curr_user:
            return "This User does not exist.", 404
        return curr_user.toJSON(), 200
    else:
        curr_user = db.session.execute(db.select(UserModel).where(UserModel.username == id)).one()
        if not curr_user:
            return "This User does not exist.", 404
        return curr_user.toJSON(), 200

@user.post("/create")
def create_user():
    """
    Create user bio, requires username and user_id, optional name and bio
    """
    try:
        data = request.get_json(force=True)
        curr_user = UserModel(
            username = data["username"],
            name = data.get("name", ""),
            bio = data.get("bio", ""),
            user_id = data["user_id"],
            public = data.get("public", True)
        )
        db.session.add(curr_user)
        db.session.commit()
        return {"text": "Success"}, 201
    except Exception as e:
        return "Failure", e, 400

@user.put("/edit")
def edit_user():
    """
    Updates user info, can update username, bio, name
    """
    try:
        data = request.get_json(force=True)
        user = db.get_or_404(UserModel, data["user_id"])
        user.username = data["username"]
        user.name = data["name"]
        user.bio = data["bio"]
        user.public = data["public"]
        db.session.commit()
        return {"text": "Success"}, 201
    except Exception as e:
        return "Failed", e,  400

@user.post("/profile-pic")
def prof_pic():
    """
    Adds prof pic location.
    """
    try:
        data = request.get_json(force=True)
        user = db.get_or_404(UserModel, data["user_id"])
        user.profile_pic = data["path"]
        db.session.commit()
        return {"text": "success"}, 201
    except Exception as e:
        return e, 400

@user.delete("/delete/<int:id>")
def delete_user(id):
    try:
        user = db.get_or_404(UserModel, id)
        db.session.delete(user)
        db.session.commit()
        return {"text": "Success"}, 200
    except:
        return "Failed", 400

@user.post("/follow")
def follow_request():
    """
    Performs follow request from one user to another.
    """
    data = request.get_json(force=True)
    if data is not None:
        # try:
            followee = db.get_or_404(UserModel, data["followee_id"])
            if followee.public:
                a = SocialRelationships(follower_id = data["user_id"], followee_id=followee.user_id, status="accepted", last_update=datetime.now(timezone.utc))
            else:
                a = SocialRelationships(follower_id=data["user_id"], followee_id=followee.user_id, status="pending", last_update=datetime.now(timezone.utc))
            db.session.add(a)
            db.session.commit()
            # Send message to notification service of follow request
            return {"text": "Success"}, 201
        # except KeyError as e:
        #     return e, 400
    return "Invalid params", 400

@user.put("/follow/accept/<int:id>")
def accept_follow(id):
    """
    Accepts a follow request.
    """
    try:
        relationship = db.get_or_404(SocialRelationships, id)
        relationship.status = "accepted"
        relationship.last_update = datetime.now(timezone.utc)
        db.session.commit()
        return {"text": "Success"}, 200
    except:
        return {"text": "Failure"}, 400    

@user.put("/follow/reject/<int:id>")
def reject_follow(id):
    """
    Rejects a follow request.
    """
    try:
        relationship = db.get_or_404(SocialRelationships, id)
        relationship.status = "rejected"
        relationship.last_update = datetime.now(timezone.utc)
        db.session.commit()
        return {"text": "Success"}, 200
    except:
        return {"text": "Failure"}, 400

@user.delete("/unfollow")
def unfollow():
    """
    Unfollows user
    """
    data = request.get_json(force=True)
    # try:
    relationship = db.session.execute(db.delete(SocialRelationships).where(
                                        SocialRelationships.followee_id == data["followee_id"]
                                    ).where(
                                        SocialRelationships.follower_id == data["user_id"]
                                    )
    )
    db.session.commit()
    return {"text": "Success"}, 200
    # except:
    #     return "Failure", 400


@user.get("/followers/get/<int:id>/<int:main_id>")
def get_followers(id, main_id):
    """
    Gets all followers of user
    """
    # try:
        # user = db.get_or_404(UserModel, id)
        # if user:
        #     followers = [{"id": follower.user_id, "username": follower.username, "name": follower.name} for follower in user.followers]
        # results = db.session.execute(db.select(SocialRelationships).where(
        #     SocialRelationships.follower_id == id
        # ).order_by(SocialRelationships.follower_id))
    stmt = text(f"""SELECT
            public.user.name AS name,
            public.user.user_id AS id,
            public.user.username AS username,
            public.user.profile_pic AS profile_pic,
            public.social_relationships.status,
            COALESCE(r.status, 'new') AS is_following
        FROM
            public.user
        JOIN
            public.social_relationships ON public.user.user_id = public.social_relationships.follower_id
        LEFT JOIN
            social_relationships r ON public.user.user_id = r.followee_id AND r.follower_id = {main_id}
        WHERE
            public.social_relationships.followee_id = {id}""")

    # stmt = db.select(UserModel.user_id, SocialRelationships.status, UserModel.name, UserModel.username).join(SocialRelationships, SocialRelationships.follower_id == UserModel.user_id).where(SocialRelationships.followee_id == id)
    results = db.session.execute(stmt)
    return [result._asdict() for result in results.all()], 200
    # except Exception as e:
    #     return e, 400

@user.get("/following/get/<int:id>/<int:main_id>")
def get_following(id, main_id):
    """
    Gets all followed users of user
    """
    # try:
    stmt = text(f"""SELECT
            public.user.name AS name,
            public.user.user_id AS id,
            public.user.username AS username,
            public.user.profile_pic AS profile_pic,
            public.social_relationships.status,
            COALESCE(r.status, 'new') AS is_following
        FROM
            public.user
        JOIN
            public.social_relationships ON public.user.user_id = public.social_relationships.followee_id
        LEFT JOIN
            social_relationships r ON public.user.user_id = r.followee_id AND r.follower_id = {main_id}
        WHERE
            public.social_relationships.follower_id = {id}""")
    # stmt = db.select(UserModel.user_id, SocialRelationships.status, UserModel.name, UserModel.username).join(SocialRelationships, SocialRelationships.followee_id == UserModel.user_id).where(SocialRelationships.follower_id == id)
    results = db.session.execute(stmt)
        # .where(
        #     SocialRelationships.follower_id == id
        # ).where(
        #     SocialRelationships.status == "accepted"
        # ).order_by(SocialRelationships.followee_id))
    rows = results.all()
    return [result._asdict() for result in rows], 200
    # except Exception as e:
        # return e, 400

@user.get("/search")
def search():
    query = request.args.get('query')
    page = request.args.get('page', 1)
    sep = "<->"
    rules = or_(func.lower(UserModel.name).like(f"%{query.lower()}%"),
                func.lower(UserModel.username).like(f"%{query.lower()}%")
            )

    
    statement = db.select(UserModel.user_id, UserModel.username, UserModel.name, UserModel.profile_pic).where(rules).limit(15).offset((int(page) - 1) * 15)
    print(statement)
    results = list(db.session.execute(statement))
    return [dict(result._mapping) for result in results], 200


# TESTING ROUTE FUNCTION
@user.get("/test")
def test():
    db.drop_all()
    db.create_all()
    u2 = UserModel(username='jacob')
    u3 = UserModel(username='james')
    u4 = UserModel(username='victor')

    u1 = UserModel(username='david', followers=[u2, u3, u4])

    db.session.add_all([u1, u2, u3, u4])
    db.session.commit()

    print(u1.followers)  # [<User jacob>, <User james>, <User victor>]
    print(u1.followers[0].following)  # [<User david>]
    print(u1.following)
    return "nice"
