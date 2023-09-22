from flask import jsonify, request, Blueprint
from models import db, guard, AuthModel
from datetime import datetime, timezone
from flask_praetorian import exceptions
from sqlalchemy.exc import IntegrityError

auth = Blueprint("auth", __name__)

@auth.post("/login")
def login():
    req = request.get_json(force=True)
    
    username = req.get("username")
    password = req.get("password")
    if "@" in username:
        curr_user = db.session.query(AuthModel).filter(AuthModel.email == username).one()
        username = curr_user.username
    else:
        curr_user = db.session.query(AuthModel).filter(AuthModel.username == username).one()
    if curr_user is None:
        return "No user found", 404 
    verified = curr_user.verify_password(username, password)
    if verified is None:
        return exceptions.AuthenticationError("Invalid Password"), 401
    ret = {"access_token": guard.encode_jwt_token(verified), "user": verified.toJSON()}
    return jsonify(ret), 200

@auth.post('/create')
def create_user():
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            curr_user = AuthModel(
                username = data["username"],
                password = data["password"],
                email = data["email"],
                created_at = datetime.now(timezone.utc)
            )
            db.session.add(curr_user)
            db.session.commit()
            return {"access_token": guard.encode_jwt_token(curr_user)}, 201
        except IntegrityError as e:
            if "username" in e._message():
                return "Username already exists", 403
            else:
                return "Email already exists", 403
    return {"status": "failure"}, 400

@auth.post('/verify')
def verify():
    try:
        encoded_jwt = request.headers["Authorization"]
    except:
        return "Missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    decoded = guard.extract_jwt_token(encoded_jwt)

    return decoded, 200


