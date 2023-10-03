from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import func

db = SQLAlchemy()

class SocialRelationships(db.Model):
    __tablename__ = "social_relationships"

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    followee_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    status = db.Column(ENUM("accepted", "pending", "rejected", "main", "new", name="status"))
    last_update = db.Column(db.DateTime(100))
    __table_args__ = (db.UniqueConstraint('follower_id', 'followee_id', name='_social_relationship_uc'),)

    def toJSON(self):
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "followee_id": self.followee_id,
            "status": self.status,
            "last_update": self.last_update 
        }
    
    def __repr__(self):
        return f"status: {self.status}"

class UserModel(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    bio = db.Column(db.String(240))
    name = db.Column(db.String(120))
    public = db.Column(db.Boolean())
    profile_pic = db.Column(db.String(240))
    following = db.relationship(
        'UserModel',  # Relationship points to the UserModel class
        secondary=SocialRelationships.__table__,  # The association table
        primaryjoin=(user_id == SocialRelationships.follower_id),
        secondaryjoin=(user_id == SocialRelationships.followee_id),
        back_populates='followers'
    )
    
    # Define the reverse relationship for followers
    followers = db.relationship(
        'UserModel',  # Relationship points to the UserModel class
        secondary=SocialRelationships.__table__,  # The association table
        primaryjoin=(user_id == SocialRelationships.followee_id),
        secondaryjoin=(user_id == SocialRelationships.follower_id),
        back_populates='following'
    )
    # prof_pic_id = db.Column(db.Integer, db.ForeignKey("media.photo_id")) -- Have prof pic uri to access prof pic from image storage

    def toJSON(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "followers": db.session.scalar(db.select(func.count(SocialRelationships.id)).where(SocialRelationships.followee_id == self.user_id).where(SocialRelationships.status == 'accepted')),
            "following": db.session.scalar(db.select(func.count(SocialRelationships.id)).where(SocialRelationships.follower_id == self.user_id).where(SocialRelationships.status == 'accepted')),
            "name": self.name,
            "bio": self.bio,
            "public": self.public,
            "profile_pic": self.profile_pic
        }


    def __repr__(self) -> str:
      return f"User(id={self.user_id!r}, name={self.name!r}, username={self.username!r}, bio={self.bio!r})"