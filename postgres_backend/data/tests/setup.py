from django.contrib.auth.models import User

import os
import json

import data.models as db_models

class TestCase:
  '''Holds all data from the api_test_cases.csv file.'''
  def __init__(self, row):
    self.test_case = row[0]
    self.test_id = row[1]
    self.url = row[2]
    self.method = row[3]
    self.request = json.loads(row[4]) if row[4] else {}
    self.username = row[5]
    self.status_code = row[6]
    self.full_response = json.loads(row[7]) if row[7] else {}  
    self.json_expression = row[8]
    self.parsed_response = json.loads(row[9]) if row[9] else {} 

class TestCases:
  '''Read in all the test cases in the api_test_cases.csv file and parse them into
  a dictionary keyed by test case name.'''
  def __init__(self):
    self.test_case_path = f"{os.environ['CUSTOM_FF_PATH']}/common/api_test_cases.csv"
    with open(self.test_case_path) as test_case_file:
      self.test_case_data = test_case_file.read().splitlines()
    if not self.test_case_data:
      raise ValueError("The test case data csv file is empty.")
    self.test_case_data = self.test_case_data[1:]
    self.test_cases = {}
  def get(self):
    for row in self.test_case_data:
      row = row.split('\t')
      this_test_case = TestCase(row)
      case_name = this_test_case.test_case
      if case_name not in self.test_cases:
        self.test_cases[case_name] = []
      self.test_cases[case_name].append(this_test_case)
    return self.test_cases  

class TestData:
  '''A single point to create and reference data needed during testing.'''
  def __init__(self):
    self.user = [row for row in User.objects.all()]
    self.league = [] 
    self.leaguestat = []
    self.lineup = []
    self.member = []
    self.statcondition = []
    # map for string -> class name lookups
    self.models = {'League': db_models.League, 'LeagueStat': db_models.LeagueStat, 
      'Lineup': db_models.Lineup, 'Member': db_models.Member, 
      'StatCondition': db_models.StatCondition}   
  def create(self, model_name, **kwargs):
    model = self.models[model_name]
    data = model.objects.create(**kwargs)
    getattr(self, model_name.lower()).append(data)