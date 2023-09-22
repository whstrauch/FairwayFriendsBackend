from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM


db = SQLAlchemy()

class CourseModel(db.Model):
    __tablename__ = "course"

    course_id = db.Column(db.Integer, primary_key=True)
    facility_name = db.Column(db.String(120))
    course_name = db.Column(db.String(120))
    formatted_address = db.Column(db.String(240))
    longitude = db.Column(db.Float(10))
    latitude = db.Column(db.Float(10))
    course_city = db.Column(db.String(240))
    course_state = db.Column(db.String(40))

    tees = db.relationship('TeesModel', back_populates='course', lazy=True)

    def toJSON(self):
        return {
            "course_id": self.course_id,
            "facility_name": self.facility_name,
            "course_name": self.course_name,
            "course_city": self.course_city,
            "course_state": self.course_state,
            "tees": [{"tee_name": tee.tee_name, "tee_id": tee.tee_set_id} for tee in self.tees]
        }

    def __repr__(self) -> str:
        return f'CourseID: {self.course_id}'

class TeesModel(db.Model):
    __tablename__ = "tees"

    tee_set_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    tee_name = db.Column(db.String(50))
    num_holes = db.Column(db.Integer)
    total_yardage = db.Column(db.Integer)
    total_par = db.Column(db.Integer)

    course = db.relationship('CourseModel', back_populates="tees")

    ratings = db.relationship('RatingsModel', back_populates="tee", lazy=True)
    holes = db.relationship('HolesModel', back_populates="tee", lazy=True)
    
    def toJSON(self):
        return {
            "tee_name": self.tee_name,
            "num_holes": self.num_holes,
            "total_yardage": self.total_yardage,
            "total_par": self.total_par,
            "ratings": [rating.toJSON() for rating in self.ratings],
            "holes": [hole.toJSON() for hole in self.holes]
        }

    def __repr__(self):
        return f'Tee name: {self.tee_name}'

class HolesModel(db.Model):
    __tablename__ = "holes"

    hole_id = db.Column(db.Integer, primary_key=True)
    tee_set_id = db.Column(db.Integer, db.ForeignKey('tees.tee_set_id'), nullable=False, primary_key=True)
    hole_number = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer)
    par = db.Column(db.Integer)
    allocation = db.Column(db.Integer, nullable=True)

    tee = db.relationship('TeesModel', back_populates='holes', lazy=True)

    def toJSON(self):
        return {
            "hole_number": self.hole_number,
            "length": self.length,
            "par": self.par,
            "allocation": self.allocation
        }

    def __repr__(self) -> str:
        return f'HoleID: {self.hole_id}'

class RatingsModel(db.Model):
    __tablename__ = "rating"

    rating_id = db.Column(db.Integer, primary_key=True)
    tee_set_id = db.Column(db.Integer, db.ForeignKey('tees.tee_set_id'), nullable=False)
    rating_type = db.Column(ENUM("Total", "Back", "Front", name="ratingType"))
    course_rating = db.Column(db.Numeric(precision=4, scale=1))
    slope_rating = db.Column(db.Integer)
    bogey_rating = db.Column(db.Numeric(precision=4, scale=1))

    tee = db.relationship('TeesModel', back_populates='ratings', lazy=True)

    def toJSON(self):
        return {
            "rating_type": self.rating_type,
            "course_rating": self.course_rating,
            "slope_rating": self.slope_rating,
            "bogey_rating": self.bogey_rating
        }

    def __repr__(self) -> str:
        return f'CourseRating: {self.course_rating}'




