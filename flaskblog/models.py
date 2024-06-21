from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from flaskblog import db, login_manager
from flask import current_app
from flask_login import UserMixin

# This decorator is used to register a callback function with Flask-Login's 
# user_loader. The function is called by Flask-Login to retrieve a user from 
# the user ID stored in the session.

# The function takes a single argument, user_id, which is the user ID stored 
# in the session. It should return a User object that corresponds to the user 
# ID.
#
# In this case, the function uses SQLAlchemy to query the database for a 
# User object with the given user ID. It then returns the User object.
#
# If the User object is not found, the function returns None.
@login_manager.user_loader
def load_user(user_id):
    # Query the database for a User object with the given user ID.
    # The int() function is used to convert the user ID from a string to an integer.
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)


    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except (BadSignature, SignatureExpired):
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    

    
