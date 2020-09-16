# -*- coding: utf-8 -*-
from flask_login import login_user, logout_user
from flaskr.security import get_user, compare_hash

from .custom_view import CustomView

class Session(CustomView):
  def post(self):
    required_params = ['username', 'password']
    if not self.check_required_params(required_params):
      return self.return_json()
    username = self.get_request_data('username')
    password = self.get_request_data('password')
    
    user = get_user(username=username)

    if user and compare_hash(user.password, password):
      login_user(user)
      return self.return_json()
    else:
      self.add_response_error(self.errors.bad_data('username and/or password'))
      return self.return_json()
  def delete(self):
    logout_user()
    return self.return_json()