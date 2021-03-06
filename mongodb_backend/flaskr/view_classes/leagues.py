# -*- coding: utf-8 -*-
from mongodb_backend.flaskr.view_classes.custom_view import CustomView
from mongodb_backend.flaskr import models
from common.hashing import generate_hash

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
    elif len(models.League.objects(name=new_league_name)):
      self.add_response_error(self.errors.name_taken('League name'))
      self.change_response_status(400)
      return self.return_json()
    else:
      password = generate_hash(password1)
      league = models.League(name=new_league_name, password=password1).save()
      # the user object returned in Flask Login is not the correct type for 
      # the ReferenceField so this explicit lookup is necessary
      user = models.User.objects.get(username=self.user.username)
      member = models.Member(user=user, league=league, admin=True).save()
      return self.return_json()