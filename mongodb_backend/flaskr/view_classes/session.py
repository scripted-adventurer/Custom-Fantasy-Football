# -*- coding: utf-8 -*-
from .custom_view import CustomView

class Session(CustomView):
  def post(self):
    required_params = ['username', 'password']
    if not self.check_required_params(required_params):
      return self.return_json()
    username = self.get_request_data('username')
    password = self.get_request_data('password')
    user = authenticate(self.request, username=username, password=password)
    if user is not None:
      login(self.request, user)
      return self.return_json()
    else:
      self.add_response_error(self.errors.bad_data('username and/or password'))
      return self.return_json()
  def delete(self):
    logout(self.request)
    return self.return_json()
