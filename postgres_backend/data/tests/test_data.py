import data.models as db_models
from django.contrib.auth.models import User

class TestData:
  '''A single source of various parameters and functions used in Django's built
  in testing for models and views.'''
  def __init__(self):
    self.user = [row for row in User.objects.all()]
    self.league = [row for row in db_models.League.objects.all()] 
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