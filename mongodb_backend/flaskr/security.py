from flask_login import UserMixin
from mongoengine import *
from werkzeug.security import generate_password_hash, check_password_hash

class User(Document, UserMixin):
  '''Represents one user of the global web application. One user can be in 
  multiple leagues (see Member). Used by Flask Login for authentication and 
  authorization.'''
  username = StringField(max_length=255, required=True, unique=True)
  email = StringField(max_length=255)
  password = StringField(max_length=255, required=True)
  active = BooleanField(default=True)

  def __repr__(self):
    return f"{{'model': 'User', 'username': '{self.username}'}}"
  def __str__(self):
    return f"{{User {self.username}}}"
  def __eq__(self, other):
    if isinstance(other, User):
      return (self.username == other.username)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(('User', self.username)) 
  def get_id(self):
    return self.username

def get_user(self, username):
  response = User.objects(username=username)
  if len(data) == 1:
    return response[0]
  else:
    return None

def generate_hash(password):
  salted_password = password + os.environ['PASSWORD_SALT']
  return generate_password_hash(salted_password)

def compare_hash(password, hashed_password):
  salted_password = password + os.environ['PASSWORD_SALT']
  return check_password_hash(salted_password, hashed_password)      