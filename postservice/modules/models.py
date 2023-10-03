from flask_sqlalchemy import SQLAlchemy
import time

db = SQLAlchemy()

class MediaModel(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    path = db.Column(db.String(240), nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    post = db.relationship("PostModel", back_populates="media")

    def toJSON(self):
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height
        }

    def __repr__(self) -> str:
        return f"Tag: {self.post_id} : {self.path}"

class TagsModel(db.Model):
    __tablename__ ="tags"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(120))
    post = db.relationship("PostModel", back_populates="tags")

    def toJSON(self):
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "user_name": self.user_name
        }

    def __repr__(self) -> str:
        return f"Tag: {self.post_id} : {self.user_id}"
    

class LikesModel(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False) #id of post that was liked
    user_id = db.Column(db.Integer, nullable=False) #id of user who liked
    timestamp = db.Column(db.DateTime(100), nullable=False)
    post = db.relationship("PostModel", back_populates="likes")
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),)

    def toJSON(self):
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        }

    def __repr__(self) -> str:
        return f"Like: {self.id}"

class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(240), nullable=False)
    timestamp = db.Column(db.DateTime(100), nullable=False)
    post = db.relationship("PostModel", back_populates="comments")

    def toJSON(self):
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "comment": self.comment
        }

    def __repr__(self) -> str:
        return f"Comment: {self.id}"



class PostModel(db.Model):
    # Holds basic user info: username, password, first name, last
    # name, email
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable=False) # Represents user_id from user table
    course_id = db.Column(db.Integer, nullable=False) # Represents course_id from course table
    course_name = db.Column(db.String(120))
    title = db.Column(db.String(120))
    caption = db.Column(db.String(480))
    ratio = db.Column(db.Float(5))
    date = db.Column(db.DateTime(100), nullable=False)
    tags = db.relationship("TagsModel", back_populates='post', cascade="all, delete, delete-orphan")
    likes = db.relationship("LikesModel", back_populates='post', cascade="all, delete, delete-orphan")
    comments = db.relationship("CommentModel", back_populates='post', cascade='all, delete, delete-orphan')
    media = db.relationship("MediaModel", back_populates='post', cascade="all, delete, delete-orphan")

    def toJSON(self):
        return {
            "id": self.id,
            "poster_id": self.user_id,
            "course_id": self.course_id,
            "course_name": self.course_name,
            "title": self.title,
            "caption": self.caption,
            "ratio": self.ratio,
            "likes": [like.toJSON() for like in self.likes], #This could create performance issues, milions of likes -> unlikely this happens anyways, deal w later
            "comments": [comment.toJSON() for comment in self.comments], #This could create performance issues
            "tags": [tag.toJSON() for tag in self.tags],
            "date": self.date.isoformat(),
            "media": [img.toJSON() for img in self.media]
        }

    def __repr__(self) -> str:
        return f"User: {self.id}"

