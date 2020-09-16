from flask_login import UserMixin
from mongoengine import *
from werkzeug.security import generate_password_hash, check_password_hash

import os

class User(Document, UserMixin):
  '''Represents one user of the global web application. One user can be in 
  multiple leagues (see Member). Used by Flask Login for authentication and 
  authorization.'''
  username = StringField(max_length=255, required=True, unique=True)
  email = StringField(max_length=255)
  password = StringField(max_length=255, required=True)
  active = BooleanField(default=True)
  
  @property
  def is_active(self):
    return self.active

  def __repr__(self):
    return f"{{'model': 'User', 'username': '{self.username}'}}"
  def __str__(self):
    return str(self.id)   # necessary for MongoEngine to work properly 
  def __hash__(self):
    return hash(('User', self.id)) 
  def set_password(self, password):
    self.password = generate_hash(password)  

def get_user(username):
  response = User.objects(username=username)
  if len(response) == 1:
    return response[0]
  else:
    return None

def generate_hash(password):
  return generate_password_hash(password)

def compare_hash(pwhash, password):
  return check_password_hash(pwhash, password)      