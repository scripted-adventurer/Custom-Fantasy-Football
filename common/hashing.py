# -*- coding: utf-8 -*-

'''A single source to change the hashing methods used throughout the application.
These are used for user and league passwords in the MongoDB backend, and just 
league passwords in the Django backend.'''

from werkzeug.security import generate_password_hash, check_password_hash

def generate_hash(password):
  return generate_password_hash(password)

def compare_hash(pwhash, password):
  return check_password_hash(pwhash, password)