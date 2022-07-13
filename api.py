import re
import bcrypt
import uuid
from db_model import DB_User, DB_Post

class API:
    def __init__(self, db):
        self.db = db

    def __verify_email_address(self, address):
        result =  re.fullmatch(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", address)
        if result:
            return address
        return None

    def __create_uuid(self):
        return str(uuid.uuid1())

    def __verify_user(self, request):
        session_key = request.cookies.get("session_key")
        if session_key:
            try:
                return DB_User.query.filter(DB_User.session_key == session_key).one()
            except Exception as e:
                pass
            return None

    def user_current(self, request):
        return self.__verify_user(request)

    def user_register(self, request):
        if self.__verify_user(request):
            return { "code": 403, "message": "You are already logged in." }
        
        user_username = re.sub(r"\W+", "", request.values["username"])
        if DB_User.query.filter_by(username=user_username).first():
            return { "code": 409, "message": "User already exists." }
        user_email = self.__verify_email_address(request.values["email"])
        if not user_email:
            return { "code": 400, "message": "Email is not valid" }
        user_password = request.values["password"].encode()
        user_password_hash = bcrypt.hashpw(user_password, bcrypt.gensalt())
        user_session_key = self.__create_uuid()

        user = DB_User(username=user_username,
                        display_name=user_username,
                        password_hash=user_password_hash,
                        email=user_email,
                        session_key=user_session_key)

        self.db.session.add(user)
        self.db.session.commit()

        return { "code": 201, "session_key": user_session_key }

    def user_login(self, request):
        if self.__verify_user(request):
            return { "code": 403, "message": "You are already logged in." }

        user_username = re.sub(r"\W+", "", request.values["username"])
        user = DB_User.query.filter_by(username=user_username).first()

        credentials_check = True
        if not user:
            credentials_check = False
        else:
            user_password = request.values["password"].encode()
            user_password_hash = bcrypt.hashpw(user_password, user.password_hash)
            if not user_password_hash == user.password_hash:
                credentials_check = False
        if not credentials_check:
            return { "code": 400, "message": "Incorrect username or password." }

        user_session_key = self.__create_uuid()
        user.session_key = user_session_key

        self.db.session.commit()

        return { "code": 200, "session_key": user_session_key }

    def post_create(self, request):
        post_user = self.__verify_user(request)
        if not post_user:
            return { "code": 403, "message": "You are not logged in." }

        post_text = request.values["text"]
        if not post_text or len(post_text) <= 0:
            return { "code": 400, "message": "Post cannot be blank." }
        if len(post_text) > 256:
            return { "code": 400, "message": "Please shorten your post." }

        post = DB_Post(text=post_text, author_id=post_user.id)
        self.db.session.add(post)
        self.db.session.commit()
        
        return { "code": 201 }

    def user_profile(self, request, **kwargs):
        user_id = kwargs.get("id")
        user_username = kwargs.get("username")
        if not (user_id or user_username):
            return { "code": 400, "message": "An error has occurred." }
        if user_id:
            user = DB_User.query.filter_by(id=user_id).first()
        elif user_username:
            user = DB_User.query.filter_by(username=user_username).first()
        
        if user:
            posts = DB_Post.query.filter_by(author_id=user.id).limit(10).all()
            return { "code": 200, "data": { "user": user.to_json(), "posts": [post.to_json() for post in posts] } }
        else:
            return { "code": 404, "message": "User not found." }