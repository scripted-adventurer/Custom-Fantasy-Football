# -*- coding: utf-8 -*-
import json
import os

from django.http import JsonResponse

from common.errors import Errors

class CustomView:
  '''A base class to handle servicing requests made to the API endpoints. Contains
  logic to handle checking if the requested method is supported and required request
  data is present. Derived classes overwrite those methods corresponding to the 
  HTTP methods they allow.'''
  def __init__(self, request, login_required):
    self.request = request
    self.login_required = login_required
    self.user = request.user
    self.request_data = json.loads(request.body) if request.body else {}
    self.request_method = request.method 
    self.response_data = {'success': True}
    self.response_status = 200
    self.errors = Errors()
  def method_not_allowed(self):
    self.change_response_status(405)
    self.add_response_error(self.errors.http_405())
    return self.return_json()
  def get(self):
    return self.method_not_allowed()
  def head(self):
    return self.get()
  def post(self):
    return self.method_not_allowed()
  def put(self):
    return self.method_not_allowed()
  def delete(self):
    return self.method_not_allowed()
  def options(self):
    return self.method_not_allowed()
  def trace(self):
    return self.method_not_allowed()
  def patch(self):
    return self.method_not_allowed()                
  def router(self):
    if self.login_required and not self.user.is_authenticated:
      self.change_response_status(401)
      self.add_response_error(self.errors.http_401())
      return self.return_json()
    method_map = {'GET': self.get, 'HEAD': self.head, 'POST': self.post, 
      'PUT': self.put, 'DELETE': self.delete, 'OPTIONS': self.options, 
      'TRACE': self.trace, 'PATCH': self.patch}
    return method_map[self.request_method]()
  def check_required_params(self, params, container=''):
    container = container if container else self.request_data
    valid = True
    for param in params:
      if param not in container or not container[param]:
        valid = False
        self.change_response_status(400)
        self.add_response_error(self.errors.bad_data(param))
    return valid
  def get_request_data(self, key):
    return self.request_data.get(key)   
  def add_response_error(self, error):
    self.response_data['success'] = False
    if 'errors' not in self.response_data:
      self.response_data['errors'] = [error]
    else:
      self.response_data['errors'].append(error)
  def add_response_data(self, data_key, data_value):
    self.response_data[data_key] = data_value
  def change_response_status(self, new_response_status):
    self.response_status = new_response_status
  def return_json(self):
    return JsonResponse(self.response_data, status=self.response_status)