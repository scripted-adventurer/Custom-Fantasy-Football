import os
import json

import flaskr.models as models

class Case:
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

class Cases:
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
      this_test_case = Case(row)
      case_name = this_test_case.test_case
      if case_name not in self.test_cases:
        self.test_cases[case_name] = []
      self.test_cases[case_name].append(this_test_case)
    return self.test_cases