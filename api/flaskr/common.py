# -*- coding: utf-8 -*-
import datetime
import pytz
import hashlib

class Utility:
  '''A collection of various utility functions used throughout the application.'''
  def __init__(self):
    pass
  def transform_pos(self, position):
    # maps each nfldb position to its position group (used in League)
    self.position_map = {'CB': 'DB', 'DB': 'DB', 'FS': 'DB', 'SAF': 'DB', 'SS': 
      'DB', 'DE': 'DL', 'DT': 'DL', 'NT': 'DL', 'ILB': 'LB', 'LB': 'LB', 'MLB': 
      'LB', 'OLB': 'LB', 'C': 'OL', 'LS': 'OL', 'OG': 'OL', 'OT': 'OL', 'QB': 
      'QB', 'FB': 'RB', 'RB': 'RB', 'WR': 'WR', 'TE': 'TE', 'K': 'K', 'P': 'P'}
    if position in self.position_map:
      return self.position_map[position]
    else:
      return 'UNK'
  def custom_hash(self, string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()   

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

class CurrentWeek:
  '''Calculates the NFL's current league week. Ex. week 17 of the 2019 regular 
  season. Logic was copied over from nflgame.'''
  def __init__(self):
    pass
  def _labor_day(self, year):
    """
    Labor day is always the first monday in september.
    """
    laborDay = datetime.datetime(year,9,1,tzinfo=pytz.utc)
    while laborDay.weekday() != 0:  # 0 is monday
        laborDay += datetime.timedelta(days=1)

    return laborDay
  def find(self, instant):
    """
    Using the following rules, the year, week, and phase is determined:

    year will be the current calendar year during march-december.
    year will be the current calendar year minus 1 during jan-feb.

    (This is not precisely accurate with the official NFL league year,
    but works for these purposes).

    The season schedule is determined in regard to Labor Day. When
    evaluating the schedule, we check for the Labor Day of the season
    year, not calendar year. E.g. we are past Labor Day in jan-feb,
    but not in march.

    Weeks are switched wednesdays (nfl.com used to switch the
    now deprecated score strip wednesday mornings).

    state will be PRE if Labor day is yet to occur, if today is Labor Day
    or if today is the tuesday immediately following Labor Day, state
    will be PRE.

    If today is no earlier than wednesday the week of Labor Day,
    and today is not after 17 weeks and one day from Labor Day
    (a tuesday), state will be REG.

    If today is no earlier than 17 weeks and two days from Labor day,
    state will be POST.

    Week numbers for preseason are counted backwards from Labor
    Day. For instance, if today is monday the week before Labor Day,
    the week is PRE3. Wednesday that week would be PRE4. Anything
    earlier than three weeks and five days prior to Labor Day
    (a wednesday) is considered to be PRE0 (Hall of fame). E.g. 1st of
    March would return PRE0.

    Week numbers for regular season are number of complete weeks
    from the wednesday following Labor Day + 1.

    Week numbers for post season weeks are number of complete
    weeks from the wednesday following Labor Day minus 16, and if
    more than 20 weeks has passed from the wednesday following
    Labor Day (conference finals have been played), POST4 is always
    returned, which equals to Super Bowl. E.g. a call on Feb 28 (or 29)
    would return POST4.

    """
    season_year = instant.year

    if instant.month is 1 or instant.month is 2:
      season_year -= 1

    labor_day = self._labor_day(season_year)
    regular_season_switch = labor_day + datetime.timedelta(days=2)
    postseason_switch = regular_season_switch + datetime.timedelta(weeks=17)

    # If negative (e.g. preseason), negative integer division will take
    # us "too far" from the switch. This is adjusted later.
    weeks_from_rs_switch = (instant - regular_season_switch).days / 7

    if instant < regular_season_switch:
      season_type = 'PRE'
      # 5 instead of 4 to adjust for negative integer division
      week = 5 + weeks_from_rs_switch

      if week < 0:
        week = 0

    elif instant < postseason_switch:
      season_type = 'REG'
      week = weeks_from_rs_switch + 1

    else:
      season_type = 'POST'
      week = weeks_from_rs_switch - 16

      if week > 4:
        week = 4

    return season_year, season_type, week 