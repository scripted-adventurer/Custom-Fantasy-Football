class Views:
  '''A base class to implement views that the backend inherits from. All the methods
  in this class must be implemented by the backend.'''
  def __init__(self):
    # each method should return data in one of these
    self.response = {}
    self.errors = []
  def login(self, username, password):
    return {'response': self.response, 'errors': self.errors}
  def logout(self):
    return {'response': self.response, 'errors': self.errors}
  def create_user(self, username, password1, password2):
    return {'response': self.response, 'errors': self.errors}
  def get_user(self):
    return {'response': self.response, 'errors': self.errors}  
  def delete_user(self, password1):
    return {'response': self.response, 'errors': self.errors}
  def update_user_password(self, property, data):
    return {'response': self.response, 'errors': self.errors}
  def create_league(self, new_league_name, password1, password2):
    return {'response': self.response, 'errors': self.errors}
  def get_league(self, league_name):
    return {'response': self.response, 'errors': self.errors}
  def update_league_password(self, league_name, property, data):
    return {'response': self.response, 'errors': self.errors}
  def update_league_lineup(self, league_name, property, data):
    return {'response': self.response, 'errors': self.errors} 
  def update_league_scoring(self, league_name, property, data):
    return {'response': self.response, 'errors': self.errors}
  def get_league_scores(self, league_name, season_type='', season_year='', week=''):
    return {'response': self.response, 'errors': self.errors}
  def get_league_stats(self, league_name, season_type='', season_year='', week=''):
    return {'response': self.response, 'errors': self.errors}
  def join_league(self, league_name, password):
    return {'response': self.response, 'errors': self.errors}
  def get_member_info(self, league_name):
    return {'response': self.response, 'errors': self.errors}
  def leave_league(self, league_name, password):
    return {'response': self.response, 'errors': self.errors}
  def remove_from_league(self, league_name, username):
    return {'response': self.response, 'errors': self.errors}
  def get_lineup(self, league_name):
    return {'response': self.response, 'errors': self.errors} 
  def edit_lineup(self, league_name, lineup):
    return {'response': self.response, 'errors': self.errors}   
  def player_query(self, query):
    return {'response': self.response, 'errors': self.errors} 
  def available_players(self, available):
    return {'response': self.response, 'errors': self.errors}
  def get_player(self, player_id):
    return {'response': self.response, 'errors': self.errors}
  def get_team(self, team_id):
    return {'response': self.response, 'errors': self.errors}
  def get_teams(self):
    return {'response': self.response, 'errors': self.errors}
  def get_week(self):
    return {'response': self.response, 'errors': self.errors}             
  def get_games(self, season_type='', season_year='', week=''):
    return {'response': self.response, 'errors': self.errors}
  