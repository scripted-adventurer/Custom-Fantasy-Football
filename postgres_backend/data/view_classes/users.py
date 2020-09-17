# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth import login

from data.view_classes.custom_view import CustomView
import data.models as models

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
    elif models.get_safe('User', username=username):
      self.change_response_status(400)
      self.add_response_error(self.errors.name_taken('Username'))
      return self.return_json()
    user = User.objects.create_user(username, email, password1)
    login(self.request, user)
    return self.return_json()