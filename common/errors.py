# -*- coding: utf-8 -*-
class Errors:
  '''A single source of all the various error messages returned throughout the 
  application.'''
  def __init__(self):
    pass
  def http_400(self):
    return "HTTP 400: Bad request"
  def http_401(self):
    return "Authentication is required."
  def http_403(self):
    return "HTTP 403: Forbidden"    
  def http_404(self):
    return "HTTP 404: Not found"
  def http_405(self):
    return "HTTP 405: Method not allowed"  
  def http_500(self):
    return "HTTP 500: Internal server error"  
  def bad_csrf(self):
    return "HTTP 403: Forbidden - CSRF verification failed due to a missing or invalid CSRF token."
  def unmatched_passwords(self):
    return "Passwords don't match."
  def bad_league(self):
    return "League name is invalid or you are not a member."
  def not_admin(self):
    return "That action requires admin privileges."
  def name_taken(self, name):
    return f"{name} is already taken."
  def bad_data(self, param):
    return f"{param} is missing or invalid."
  def unrecognized(self, param):
    return f"{param} is invalid or is not formatted properly."
  def locked_player(self, player_id):
    return f"Player {player_id} is currently locked for editing."