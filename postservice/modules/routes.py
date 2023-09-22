from flask import request, Blueprint
from models import db, PostModel, LikesModel, CommentModel, TagsModel, MediaModel
from datetime import datetime, timezone
from sqlalchemy import desc

post = Blueprint("post", __name__)

"""
Routes needed:
    Get post
    Create post
    Delete post
    Edit post
    Like post
    Remove like
    Add comment
    Delete comment
    Edit comment
    Add tag
    Remove tags/tag
    Update tags
"""

@post.get('/get/<int:id>')
def get_post(id):
    """
    Gets post from given id, might add ability to request lots of ids at once
    """
    try:
        post = db.get_or_404(PostModel, id)
        return post.toJSON(), 200
    except:
        "Failed", 400

@post.get('/get/user/<int:id>')
def get_user_posts(id):
    # try:
        stmt = db.select(PostModel).where(PostModel.user_id == id).order_by(desc(PostModel.date))
        print("state", stmt)
        posts = db.session.execute(stmt)
        returned = []
        for post in posts.scalars():
            print(type(post))
            returned.append(post.toJSON())
        print(returned)
        return returned, 200
    # except:
        # return "Failed", 400



@post.post('/create')
def create():
    """
    Creates post: requires user id, course id, optional title, caption, date
    """
    try:
        data = request.get_json(force=True)
        post = PostModel(
                user_id = data["user_id"],
                course_id = data["course_id"],
                course_name = data["course_name"],
                title = data.get('title', ''),
                caption = data.get('caption', ''),
                ratio = data.get('ratio', 1.4),
                date = data.get('date', datetime.now(timezone.utc)) #Have to adjust since post new and old round, should be handled in frontend
            )
        
        db.session.add(post)
        db.session.commit()
        return {"id": post.id}, 201
    except Exception as e:
        print(e)
        return "Failure", 400

@post.delete('/delete')
def delete():
    """
    Deletes post, requires post_id, user_id
    """
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        if post.user_id == int(data["user_id"]):
            try:
                db.session.delete(post)
                db.session.commit()
                return "Success", 200
            except:
                return "Failure", 400
        else:
            return "Failure", 403
    else:
        return "Must provide post_id, user_id", 400

@post.put('/edit')
def edit():
    """
    Edits post -> can only edit caption and title, requires post_id, user_id, caption, title
    """
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        if post.user_id == data["user_id"]:
            try:
                post.title = data["title"]
                post.caption = data["caption"]
                db.session.commit()
                return "Success", 201
            except:
                return "Failure", 400
        else:
            return "Failure", 403
    else:
        return "Need to provide edits", 400


@post.post('/like/add')
def like():
    """
    Add like: requires post_id, user_id
    """
    data = request.get_json(force=True)
    if data is not None:
        like = LikesModel(
            post_id = data["post_id"],
            user_id = data["user_id"],
            timestamp = datetime.now(timezone.utc)
        )
        post = db.get_or_404(PostModel, data["post_id"])
        if post.user_id == data["user_id"]:
            try:
                post.likes.append(like)
                db.session.commit()
                ## Add in message to be sent to notification service
                return "Success", 201
            except:
                return "Failure", 400
        else:
            return "Failure", 403
    return "failure", 400

@post.delete('/like/remove')
def delete_like():
    """
    Delete like: require post_id, user_id
    """
    data = request.get_json(force=True)
    if data is not None:
        try:
            post = db.get_or_404(PostModel, data["post_id"])
            post.likes = list(filter(lambda like: like.user_id == data["user_id"], post.likes))
            db.session.commit()
            return "Success", 201
        except:
            return "failure", 404
    return "failure", 400

@post.post('/comment/add')
def comment():
    """
    Add comment: provide user_id, post_id, comment text
    """
    data = request.get_json(force=True)
    if data is not None:
        try:
            comment = CommentModel(
                post_id = data["post_id"],
                user_id = data["user_id"],
                comment = data["comment"],
                timestamp = datetime.now(timezone.utc)
            )
            db.session.add(comment)
            db.session.commit()
            ## Add in message to be sent to notification service.
            return "Success", 201
        except:
            return "Failure", 400
    return "Must provide proper params", 400

@post.delete('/comment/remove')
def delete_comment():
    """
    Delete comment: provide comment_id, user_id
    """
    data = request.get_json(force=True)
    if data is not None:
        comment = db.get_or_404(CommentModel, data["comment_id"])
        if comment.user_id == data["user_id"]:
            try:
                db.session.delete(comment)
                db.session.commit()
                return "Success", 201
            except:
                return "Failure", 400
        else:
            return "Failure", 403
    return "Must provide proper params", 400

@post.put('/comment/edit')
def edit_comment():
    """
    Edit comments: provide comment_id, user_id, new_comment
    """
    data = request.get_json(force=True)
    if data is not None:
        comment = db.get_or_404(CommentModel, data["comment_id"])
        if comment.user_id == data["user_id"]:
            try:
                comment.comment = data["comment"]
                comment.timestamp = datetime.now(timezone.utc)
                db.session.commit()
                return "Success", 201
            except:
                return "Failure", 400
        else:
            return "Failure", 403
    return "Failure", 400

@post.post('/tag/add')
def add_tags():
    """
    Add tags to post: Need post_id, list of user_ids
    """
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        try:
            for user_id in data["tagged"]:
                post.tags.append(
                    TagsModel(
                        user_id=user_id,
                        post_id=post.id
                    )
                )
            db.session.commit()
            return "Success", 201
        except:
            return "Failure", 400
    return "Provide proper params", 400

@post.delete('/tag/remove')
def remove_tag():
    """
    Remove tag from post: requires post_id, users array to remove multiple tags at once.
    """
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        try:
            post.tags = list(filter(lambda tag: tag.user_id not in data["tagged"], post.tags))
            db.session.commit()
            return "Success", 201
        except:
            return "Failure", 400
    return "Provide proper params", 400

@post.put('/tag/update')
def update_tags():
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        try:
            post.tags = list(filter(lambda tag: tag.user_id in data["tagged"], post.tags))
            db.session.commit()
            return "Success", 201
        except:
            return "Failure", 400
    return "Provide proper params", 400


@post.post('/media/add')
def add_media():
    """
    Add media to post: Need post_id, list of media paths
    """
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        try:
            for path in data["media"]:
                post.media.append(
                    MediaModel(
                        path=path["path"],
                        width=path["width"],
                        height=path["height"],
                        post_id=post.id
                    )
                )
            db.session.commit()
            return "Success", 201
        except:
            return "Failure", 400
    return "Provide proper params", 400

@post.delete('/media/remove')
def remove_media():
    """
    Remove media from post: requires post_id, media array to remove multiple media at once.
    """
    data = request.get_json(force=True)
    if data is not None:
        post = db.get_or_404(PostModel, data["post_id"])
        try:
            post.media = list(filter(lambda media: media.path not in data["media"], post.media))
            db.session.commit()
            return "Success", 201
        except:
            return "Failure", 400
    return "Provide proper params", 400


