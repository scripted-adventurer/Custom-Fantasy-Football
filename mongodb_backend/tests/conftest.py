import pytest
import json 
import os
import gzip

from mongoengine import connect
from flask import current_app

from mongodb_backend.flaskr.app import create_app
from mongodb_backend.flaskr import models 
from mongodb_backend.flaskr.sync_db import SyncDB

@pytest.fixture
def app():
  app = create_app(testing=True)

  with app.app_context():
    db = connect('test', 
      host=current_app.config['MONGODB_SETTINGS']['host'], 
      port=current_app.config['MONGODB_SETTINGS']['port'], 
      username=current_app.config['MONGODB_SETTINGS']['username'], 
      password=current_app.config['MONGODB_SETTINGS']['password'])

  # seed the test database with team, player, and 2019 game data
  SyncDB().test_db_setup()

  yield app

  db.drop_database('test')

@pytest.fixture
def client(app):
  return app.test_client()    