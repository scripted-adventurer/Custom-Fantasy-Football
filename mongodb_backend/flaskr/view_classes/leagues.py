# -*- coding: utf-8 -*-
from .custom_view import CustomView
from flaskr import models

class Leagues(CustomView):
  def post(self):
    required_params = ['new_league_name', 'password1', 'password2']
    if not self.check_required_params(required_params):
      return self.return_json()
    new_league_name = self.get_request_data('new_league_name')
    password1 = self.get_request_data('password1')
    password2 = self.get_request_data('password2')
    if password1 != password2:
      self.add_response_error(self.errors.unmatched_passwords())
      self.change_response_status(400)
      return self.return_json()
    elif len(db_models.League.objects.filter(name=new_league_name)):
      self.add_response_error(self.errors.name_taken('League name'))
      self.change_response_status(400)
      return self.return_json()
    else:
      league = db_models.League.objects.create(name=new_league_name)
      league.set_password(password1)
      member = db_models.Member.objects.create(user=self.user, league=league, 
        admin=True)
      return self.return_json()