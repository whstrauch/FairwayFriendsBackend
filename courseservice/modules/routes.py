import time
from flask import jsonify, request, Blueprint
from sqlalchemy.dialects import postgresql
from models import db, CourseModel, RatingsModel, TeesModel, HolesModel
from datetime import datetime, timezone
import json
from sqlalchemy import func, and_

course = Blueprint("course", __name__)

@course.post('/massupload')
def mass_upload():
    """
    Custom route to be run once to have initial upload of all courses from files.
    JOB DONE. ROUTE KEPT FOR REFERENCE.
    """
    if 2 == 2:
        return "THIS ROUTE IS NO LONGER ALLOWED", 403

    def get_files(id):
        file = f"/Users/willstrauch/FairwayFriendsMain/python/src/courses{id}.json"
        return file

    time1 = time.perf_counter()
    for id in range(2,5):
        with open(get_files(id), 'r') as file:
            items = json.load(file)
        
        courses =[]
        tee_sets = []
        ratings = []
        holes = []
        for item in items:
            if item is not None:
                courses.append({"course_name": item.get("course_name", ""),
                    "course_id": item["course_id"],
                    "facility_name" : item.get('facility_name', None),
                    "course_city" : item.get('course_city', None),
                    "course_state" : item.get('course_state', None),
                    "formatted_address" : item.get("formatted_address", None),
                    "longitude" : item.get("longitude", None),
                    "latitude" : item.get("latitude", None)
                    })
                for tee_set in item["tee_sets"]:
                    if tee_set is not None:
                        tee_sets.append({
                                    "course_id": item["course_id"],
                                    "tee_set_id":tee_set["tee_set_id"],
                                    "tee_name" : tee_set["name"],
                                    "num_holes" : tee_set["num_holes"],
                                    "total_yardage" : tee_set["total_yardage"],
                                    "total_par" : tee_set["total_par"]
                                })
                        for rating in tee_set["ratings"]:
                            if rating is not None:
                                ratings.append({
                                    "tee_set_id": tee_set["tee_set_id"],
                                    "rating_type": rating["RatingType"],
                                    "course_rating": rating["CourseRating"],
                                    "slope_rating": rating["SlopeRating"],
                                    "bogey_rating": rating["BogeyRating"]
                                })
                        for hole in tee_set["holes"]:
                            if hole is not None:
                                holes.append({
                                    "tee_set_id": tee_set["tee_set_id"],
                                    "hole_number": hole["Number"],
                                    "hole_id": hole["HoleId"],
                                    "length": hole["Length"],
                                    "par": hole["Par"],
                                    "allocation": hole.get("Allocation")
                                 })
        
        print(f"Attempting to add courses from file {id}...")
        db.session.execute(db.insert(CourseModel), courses)
        print("Added courses!")
        print(f"Attempting to add tees from file {id}...")
        db.session.execute(db.insert(TeesModel), tee_sets)
        print("Added tees!")
        print(f"Attempting to add ratings from file {id}...")
        db.session.execute(db.insert(RatingsModel), ratings)
        print("Added ratings!")
        print(f"Attempting to add holes from file {id}...")
        db.session.execute(db.insert(HolesModel), holes)
        print("Added holes!")
        
        
        
        db.session.commit()
    time2 = time.perf_counter()
    return f"That took {time2 - time1} seconds.", 200

        
@course.get('/course/<int:id>')
def get_course(id):
    course = db.get_or_404(CourseModel, id)
    return course.toJSON(), 200

@course.get('/tee/<int:id>')
def get_tees(id):
    tee = db.get_or_404(TeesModel, id)
    return tee.toJSON(), 200

@course.get('/course/search')
def search():
    query = request.args.get('query')
    city = request.args.get('city')
    state = request.args.get('state')
    page = request.args.get('page')
    sep = "<->"
    rules = func.to_tsvector(func.concat(CourseModel.course_name, ' ', CourseModel.facility_name)).bool_op("@@")(
            func.to_tsquery(f"{sep.join(query.split())}:*")
        )
    if city is not None and city != "":
        rules = and_(rules, (func.to_tsvector(CourseModel.course_city).bool_op("@@")(
            func.to_tsquery(f"{sep.join(city.split())}:*"))
        ))
    if state is not None and state != "":
        rules = and_(rules, (func.to_tsvector(CourseModel.course_state).bool_op("@@")(
            func.to_tsquery(f"'{sep.join(state.split())}:*'")
        )))
    statement = db.select(CourseModel.course_id, CourseModel.facility_name, CourseModel.course_name, CourseModel.course_city, CourseModel.course_state).where(rules).limit(15).offset((int(page) - 1) * 15)

    results = list(db.session.execute(statement))
    return [dict(result._mapping) for result in results], 200


@course.post('/course')
def create_course():
    pass

