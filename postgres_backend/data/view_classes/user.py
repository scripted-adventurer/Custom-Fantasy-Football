# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate

from data.view_classes.custom_view import CustomView
import data.models as models

class User(CustomView):
  def get(self):
    username = self.user.username
    self.add_response_data('username', username)
    leagues = [row.league.name for row in models.Member.objects.filter(
      user=self.user)]
    self.add_response_data('leagues', leagues)
    return self.return_json()
  def delete(self):
    # must reauthenticate
    required_params = ['password']
    if not self.check_required_params(required_params):
      return self.return_json()
    password = self.get_request_data('password')
    if not authenticate(self.request, username=self.user.username, 
      password=password):
      self.add_response_error(self.errors.bad_data('password'))
      self.change_response_status(400)
      return self.return_json()
    self.user.delete()
    return self.return_json()
  def patch(self):
    required_params = ['property', 'data']
    if not self.check_required_params(required_params):
      return self.return_json()
    if self.get_request_data('property') == 'password':
      old_password = self.get_request_data('data').get('old_password')
      new_password1 = self.get_request_data('data').get('new_password1')
      new_password2 = self.get_request_data('data').get('new_password2')
      if new_password1 != new_password2:
        self.add_response_error(self.errors.unmatched_passwords())
        self.change_response_status(400)
        return self.return_json()
      elif not authenticate(self.request, username=self.user.username, 
        password=old_password):
        self.add_response_error(self.errors.bad_data('password'))
        self.change_response_status(400)
        return self.return_json()
      else:
        self.user.set_password(new_password1)
        return self.return_json()
    else:
      self.add_response_error(self.errors.bad_data('property'))
      self.change_response_status(400)
      return self.return_json()    