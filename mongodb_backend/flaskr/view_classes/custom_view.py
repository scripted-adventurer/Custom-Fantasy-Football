# -*- coding: utf-8 -*-
from flask import jsonify, Response

import json
import os

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Errors = common.Errors

class CustomView:
  '''A base class to handle servicing requests made to the API endpoints. Contains
  logic to handle checking if the required request data is present and building 
  the response.'''
  def __init__(self, request, current_user=None):
    self.request = request
    self.user = current_user
    self.request_data = request.json
    self.response_data = {'success': True}
    self.response_status = 200
    self.errors = Errors()
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
    return Response(jsonify(self.response_data), status=self.response_status, 
      mimetype='application/json')