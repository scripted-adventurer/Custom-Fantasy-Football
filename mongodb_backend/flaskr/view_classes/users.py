# -*- coding: utf-8 -*-
from flask_login import login_user

from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models
from hashing import generate_hash

class Users(CustomView):
  def post(self):
    required_params = ['username', 'password1', 'password2']
    if not self.check_required_params(required_params):
      return self.return_json()
    username = self.get_request_data('username')
    email = self.get_request_data('email')
    password1 = self.get_request_data('password1')
    password2 = self.get_request_data('password2')
    if password1 != password2:
      self.change_response_status(400)
      self.add_response_error(self.errors.unmatched_passwords())
      return self.return_json()
    # existing user with username
    elif models.User.objects(username=username).first():
      self.change_response_status(400)
      self.add_response_error(self.errors.name_taken('Username'))
      return self.return_json()
    password = generate_hash(password1)
    user = models.User(username=username, email=email, password=password).save()
    login_user(user)
    return self.return_json()