class Views:
  '''A base class to implement views that the backend inherits from. All the methods
  in this class must be implemented by the backend.'''
  def __init__(self):
    # each method should return data in one of these
    self.data = {}
    self.errors = []
  def login(self, username, password):
    return {'data': self.data, 'errors': self.errors}
  def logout(self):
    return {'data': self.data, 'errors': self.errors}
  def create_user(self, username, password1, password2):
    return {'data': self.data, 'errors': self.errors}
  def get_user(self):
    return {'data': self.data, 'errors': self.errors}  
  def delete_user(self, password1):
    return {'data': self.data, 'errors': self.errors}
  def update_user_password(self, property, data):
    return {'data': self.data, 'errors': self.errors}
  def create_league(self, new_league_name, password1, password2):
    return {'data': self.data, 'errors': self.errors}
  def get_league(self, league_name):
    return {'data': self.data, 'errors': self.errors}
  def update_league_password(self, league_name, property, data):
    return {'data': self.data, 'errors': self.errors}
  def update_league_lineup(self, league_name, property, data):
    return {'data': self.data, 'errors': self.errors} 
  def update_league_scoring(self, league_name, property, data):
    return {'data': self.data, 'errors': self.errors}
  def get_league_scores(self, league_name, season_type='', season_year='', week=''):
    return {'data': self.data, 'errors': self.errors}
  def get_league_stats(self, league_name, season_type='', season_year='', week=''):
    return {'data': self.data, 'errors': self.errors}
  def join_league(self, league_name, password):
    return {'data': self.data, 'errors': self.errors}
  def get_member_info(self, league_name):
    return {'data': self.data, 'errors': self.errors}
  def leave_league(self, league_name, password):
    return {'data': self.data, 'errors': self.errors}
  def remove_from_league(self, league_name, username):
    return {'data': self.data, 'errors': self.errors}
  def get_lineup(self, league_name):
    return {'data': self.data, 'errors': self.errors} 
  def edit_lineup(self, league_name, lineup):
    return {'data': self.data, 'errors': self.errors}   
  def player_query(self, query):
    return {'data': self.data, 'errors': self.errors} 
  def available_players(self, available):
    return {'data': self.data, 'errors': self.errors}
  def get_player(self, player_id):
    return {'data': self.data, 'errors': self.errors}
  def get_team(self, team_id):
    return {'data': self.data, 'errors': self.errors}
  def get_teams(self):
    return {'data': self.data, 'errors': self.errors}
  def get_week(self):
    return {'data': self.data, 'errors': self.errors}             
  def get_games(self, season_type='', season_year='', week=''):
    return {'data': self.data, 'errors': self.errors}
  