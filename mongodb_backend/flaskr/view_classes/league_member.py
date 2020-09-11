# -*- coding: utf-8 -*-
from .league_base import LeagueBase
from flaskr import models

class LeagueMember(LeagueBase):
  def get(self):
    if not self.check_member():
      return self.return_json()
    self.add_response_data('admin', self.member.is_admin())
    return self.return_json()
  def delete(self):
    if not self.check_member():
      return self.return_json()
    # remove requesting user
    if self.get_request_data('password'):
      # re check password for security
      if not authenticate(self.request, username=self.user.username, 
        password=self.get_request_data('password')):
        self.add_response_error(self.errors.bad_data('password'))
        self.change_response_status(400)
        return self.return_json()
      self.member.delete()
      return self.return_json()
    # remove other user
    username = self.get_request_data('username')
    if self.get_request_data('username'):
      if not self.member.is_admin():
        self.add_response_error(self.errors.not_admin())
        self.change_response_status(403)
        return self.return_json()
      to_remove = db_models.get_safe('Member', league=self.league, 
        user__username=username)
      if not to_remove:
        self.change_response_status(400)
        self.add_response_error(self.errors.bad_data('username'))
        return self.return_json()
      to_remove.delete()
      return self.return_json()
    # neither remove self nor a username was provided
    self.change_response_status(400)
    self.add_response_error(self.errors.http_400())
    return self.return_json() 