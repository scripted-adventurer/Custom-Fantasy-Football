from django.test import Client

import json
import copy
from jsonpath_ng import jsonpath, parse
import os

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Errors = common.Errors

class ViewTestRequest:
  '''Makes a test request according to the parameters provided and performs
  various validations on the response.'''
  def __init__(self, test_case, test_id, url, method, request, username, 
      status_code, full_response, json_expression, parsed_response):
    self.test_case = test_case
    self.test_id = test_id
    self.url = url
    self.method = method
    self.test_name_string = f"{test_case} {test_id} {method}"
    self.request = request if request else {}
    self.username = username
    self.expected_status_code = status_code
    self.expected_full_response = full_response
    self.json_expression = json_expression
    self.expected_parsed_response = parsed_response
    self.client = Client()
    
    if username:
      self.client.login(username=username, password='password')
    if self.method == 'GET':
      self.response = self.client.get(self.url)
    if self.method == 'HEAD':
      self.response = self.client.head(self.url)
    if self.method == 'POST':
      self.response = self.client.post(self.url, self.request, 'application/json')
    if self.method == 'PUT':
      self.response = self.client.put(self.url, self.request, 'application/json')
    if self.method == 'DELETE':
      self.response = self.client.delete(self.url, self.request, 'application/json')
    if self.method == 'OPTIONS':
      self.response = self.client.options(self.url, self.request, 'application/json')
    if self.method == 'TRACE':
      self.response = self.client.trace(self.url)
    if self.method == 'PATCH':
      self.response = self.client.patch(self.url, self.request, 'application/json')
  def _get_response(self):
    self.received_status_code = self.response.status_code
    self.response_content = (json.loads(self.response.content) if 
      (self.response.content) else {})
  def _check_status(self):
    if int(self.expected_status_code) != self.received_status_code:
      print(f"ERROR: {self.test_name_string} - status code failure. Expected: "
        f"{self.expected_status_code} Got: {self.received_status_code}")
      return False
    return True
  def _check_response(self):
    if self.expected_full_response != self.response_content:
      print(f"ERROR: {self.test_name_string} - response failure. Expected: "
        f"{self.expected_full_response} Got: {self.response_content}")
      return False
    return True 
  def _check_json_expression(self):
    json_expression = parse(self.json_expression)
    matches = [match.value for match in json_expression.find(self.response_content)]
    if matches != self.expected_parsed_response:
      print(f"ERROR: {self.test_name_string} - json expression failure. Expected: "
        f"{self.expected_parsed_response} Got: {matches}")
      print(f"Full response: {self.response_content}")
      return False
    return True 
  def run(self):
    self._get_response()
    valid = self._check_status()
    if self.expected_full_response:
      valid = self._check_response()
    if self.expected_parsed_response:
      valid = self._check_json_expression()
    return valid  