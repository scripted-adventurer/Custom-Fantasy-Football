from flask import Response, jsonify

from config.py import USE_MONGO_BACKEND
from mongodb_backend import views as mongo_views
from postgres_backend import views as postgres_views

class Servicer:
  '''Services requests made to the API. Takes care of checking for required input,
  makes the associated request to the backend, and formats the response (handling
  errors if necessary).'''
  def __init__(self, endpoint, request, required_data=[], url_data={}):
    self.endpoint = endpoint
    self.request = request 
    if request.method == 'GET':
      self.request_data = request.args
    else:
      self.request_data = request.json   
    self.required_data = required_data
    self.url_data = url_data
    self.response = {'success': True}
    self.errors = []
    self.response_status = 200
    # select the correct backend module
    if USE_MONGO_BACKEND:
      self.view = mongo_views.View()
    else:
      self.view = postgres_views.View()
    self._data_is_present()
    if self.response['success']:
      self._call_backend()  
  def _data_is_present(self):
    # checks that the request contains all required data.
    for param in self.required_data:
      if param not in self.request_data:
        self.response_status = 400
        self.errors.append(f"Missing data for {param}")
  def _call_backend(self):
    # makes the request to the backend and updates it's response according to
    # the data received
    for key, value in self.url_data:
      self.request_data[key] = value
    response = getattr(self.view, self.backend_endpoint)(**self.request_data)
    self.errors += response['errors']
    for key, value in response['data']:
      self.response[key] = value 
  def response(self):
    if self.errors:
      self.response['success'] = False
      self.response['errors'] = self.errors
    return Response(jsonify(self.response), status=self.response_status, 
      mimetype='application/json')  