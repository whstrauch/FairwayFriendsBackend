import json
from flask import request, Blueprint
import requests, os
from authsvc import validate
from coursesvc import course_request

course_routes = Blueprint("course", __name__)

@course_routes.get('/course/search/<string:query>')
def search_courses(query):
    """
    Search for courses based on query. Return list of courses (add pagination?)
    """
    valid, err = validate.token(request)
    if err:
        return err
    print('found')
    results = course_request.request(f'course/search?{query}', method="GET")
    print('bad')
    if results.status_code == 200:
        return results.json(), 200
    else:
        return "Failure", 400


@course_routes.get('/course/get/<int:id>')
def get_course(id):
    """
    Get course from id.
    """
    valid, err = validate.token(request)
    if err:
        return err
    
    course = course_request.request(f'course/{id}', method="GET")
    if course.status_code == 200:
        return course.json(), 200
    else:
        return "Failure", 400

@course_routes.get('/course/tee/<int:id>')
def get_tee(id):
    """
    Get tee from id.
    """
    valid, err = validate.token(request)
    if err:
        return err
    
    tee = course_request.request(f'tee/{id}', method="GET")
    if tee.status_code == 200:
        return tee.json(), 200
    else:
        return "Failure", 400
