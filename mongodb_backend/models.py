import statmap

def convert_yard_line(yard_line, possession_team):
  # extract team ID and yardline ex. "GB 25" -> ['GB', 25]
  try:
    yard_line = yard_line.split(' ')
    team = yard_line[0]
    yard_value = int(yard_line[1])
  except:
    return "N/A"  
  # team's own yard line is negative, opponent's is positive
  # ex. GB on the GB 25 = -25, GB on the CHI 25 = 25
  if team == possession_team:
    return -1 * yard_value
  else:
    return yard_value

class Game:
  '''Represents a single NFL game in a season and provides a logical mapping 
  between fields found in the NFL API and fields used in the 'game' collection of
  the MongoDB database.'''
  def __init__(self, game_info, game_detail):
    game_info = game_info["node"]
    game_detail = game_detail["data"]["viewer"]["gameDetail"]
    # use this as the MongoDB collection ID
    self._id = game_info["esbId"]
    self.week = {"season_type": game_info["week"]["seasonType"], "season_year":
      game_info["week"]["seasonValue"], "week": game_info["week"]["weekValue"]}
    self.start_time = game_detail["gameTime"]
    self.phase = game_detail["phase"]
    self.attendance = game_detail["attendance"]
    self.stadium = game_detail["stadium"]
    self.home_score = {
      "total": game_detail["homePointsTotal"], 
      "Q1": game_detail["homePointsQ1"], 
      "Q2": game_detail["homePointsQ2"], 
      "Q3": game_detail["homePointsQ3"], 
      "Q4": game_detail["homePointsQ4"], 
      "overtime": game_detail["homePointsOvertimeTotal"]
    }
    self.away_score = {
      "total": game_detail["visitorPointsTotal"], 
      "Q1": game_detail["visitorPointsQ1"], 
      "Q2": game_detail["visitorPointsQ2"], 
      "Q3": game_detail["visitorPointsQ3"], 
      "Q4": game_detail["visitorPointsQ4"], 
      "overtime": game_detail["visitorPointsOvertimeTotal"]
    }
    self.home_team = {
      "name": game_detail["homeTeam"]["nickName"],
      "id": game_detail["homeTeam"]["abbreviation"]
    }
    self.away_team = {
      "name": game_detail["visitorTeam"]["nickName"],
      "id": game_detail["visitorTeam"]["abbreviation"]
    }
    try:
      self.weather = game_detail["weather"]["shortDescription"]
    except:
      self.weather = "N/A"  
    self.drives = self._get_drives(game_detail["drives"])
    self.plays = self._get_plays(game_detail["plays"])
  def __repr__(self):
    return f"models.Game(id={self._id})"
  def __str__(self):
    return f"{{Game {self._id}}}"
  def __eq__(self, other):
    if isinstance(other, Game):
      return (self.__dict__ == other.__dict__)
    else:
      return NotImplemented
  def __hash__(self):
    return hash(self._id)
  def _get_drives(self, drives):
    return [Drive(drive).as_dict() for drive in drives]
  def _get_plays(self, plays):
    return [Play(play).as_dict() for play in plays]
  def as_dict(self):
    return self.__dict__  
  

class Drive:
  '''Represents a single drive in a given NFL game and provides a logical mapping
  between the fields found in the NFL API and the 'drives' field of the 'game'
  collection found in the MongoDB database.'''
  def __init__(self, drive):
    self.start_quarter = drive["quarterStart"]
    self.start_transition = drive["startTransition"]
    self.start_time = drive["gameClockStart"]
    self.end_quarter = drive["quarterEnd"]
    self.end_transition = drive["endTransition"]
    self.end_time = drive["gameClockEnd"]
    self.possession_team = {
      "name": drive["possessionTeam"]["nickName"] if drive["possessionTeam"] else "",
      "id": drive["possessionTeam"]["abbreviation"] if drive["possessionTeam"] else ""
    }
    self.possession_time = drive["timeOfPossession"]
    self.first_downs = drive["firstDowns"]
    self.penalty_yards = drive["yardsPenalized"]
    self.yards_gained = drive["yards"]
    self.play_count = drive["playCount"]
    self.start_yardline = self._convert_yard_line(drive["startYardLine"], 
      self.possession_team['id'])
    self.end_yardline = self._convert_yard_line(drive["endYardLine"], 
      self.possession_team['id'])
  def __repr__(self):
    return f"models.Drive({self.__dict__}))"
  def __str__(self):
    return f"models.Drive({self.__dict__}))"
  def __eq__(self, other):
    if isinstance(other, Drive):
      return (self.__dict__ == other.__dict__)
    else:
      return NotImplemented 
  def __hash__(self):
    values = []
    for value in self.__dict__.values():
      if isinstance(value, dict):
        for sub_value in value.values():
          values.append(sub_value)
      else:
        values.append(value)  
    return hash(tuple(values))
  def _convert_yard_line(self, yard_line, possession_team):
    return convert_yard_line(yard_line, possession_team) 
  def as_dict(self):
    return self.__dict__    

class Play:
  '''Represents a single play in a given NFL game and provides a logical mapping
  between the fields found in the NFL API and the 'plays' field of the 'game' 
  collection found in the MongoDB database.'''
  def __init__(self, play):
    self.drive_id = play["driveSequenceNumber"]
    self.quarter = play["quarter"]
    self.possession_team = {
      "name": play["possessionTeam"]["nickName"] if play["possessionTeam"] else "",
      "id": play["possessionTeam"]["abbreviation"] if play["possessionTeam"] else ""
    }
    self.start_time = play["clockTime"]
    self.end_time = play["endClockTime"]
    self.down = play["down"]
    self.yards_to_go = play["yardsToGo"]
    self.yards_gained = play["yards"]
    self.description = play["playDescription"]
    self.first_down = play["firstDown"]
    self.penalty = play["penaltyOnPlay"]
    self.play_type = play["playType"]
    self.scoring_play_type = play["scoringPlayType"]
    self.play_clock = play["playClock"]
    self.time_of_day = play["timeOfDay"]
    self.start_yardline = self._convert_yard_line(play["yardLine"], 
      self.possession_team['id'])
    self.end_yardline = self._convert_yard_line(play["endYardLine"], 
      self.possession_team['id'])
    # contains a mapping of stat names to summed stat values for all stats in the play
    self.aggregate = {}
    # contains a list of objects with player IDs and stat names/values
    self.player_stats = []
    self._parse_play_stats(play["playStats"])
  def __repr__(self):
    return f"models.Play({self.__dict__}))"
  def __str__(self):
    return f"models.Play({self.__dict__}))"
  def __eq__(self, other):
    if isinstance(other, Play):
      return (self.__dict__ == other.__dict__)
    else:
      return NotImplemented 
  def __hash__(self):
    return hash((self.drive_id, self.quarter, self.possession_team["name"],
      self.possession_team["id"], self.start_yardline, self.start_time, 
      self.end_yardline, self.end_time, self.down, self.yards_to_go, 
      self.yards_gained, self.description, self.first_down, self.penalty, 
      self.play_type, self.scoring_play_type, self.play_clock, self.time_of_day))
  def _convert_yard_line(self, yard_line, possession_team):
    return convert_yard_line(yard_line, possession_team)
  def _parse_play_stats(self, play_stats):
    # turn the list of play stats with numeric IDs into player level and 
    # aggregate play level human readable stats  
    temp_player_stats = {}
    for raw_stat in play_stats:
      # convert the stat ID and yards to a dict of "stat_name": "stat_value"
      parsed_stats = statmap.values(raw_stat["statId"], raw_stat["yards"])
      for stat_name, stat_value in parsed_stats.items():
        # track combined stats for each player involved in the play
        try:
          player_id = raw_stat["gsisPlayer"]["person"]["id"]
          if player_id not in temp_player_stats:
            temp_player_stats[player_id] = {'id': player_id}
          temp_player_stats[player_id][stat_name] = stat_value
        except TypeError:
          pass
        # track aggregated stats for the entire play  
        if stat_name not in self.aggregate:
          self.aggregate[stat_name] = stat_value 
        else:
          self.aggregate[stat_name] += stat_value

    for entry in temp_player_stats.values():
      self.player_stats.append(entry)      
    
  def as_dict(self):
    return self.__dict__        