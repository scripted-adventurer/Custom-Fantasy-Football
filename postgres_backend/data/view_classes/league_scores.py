# -*- coding: utf-8 -*-
from data.view_classes.league_base import LeagueBase
import data.models as models
from data.view_classes.stat_query import StatQuery

class LeagueScores(LeagueBase): 
  def get(self):
    if not self.check_member():
      return self.return_json()
    if not self.check_season_week():
      return self.return_json()
    scoring_settings = self.league.get_scoring_settings()
    stats = StatQuery(scoring_settings=scoring_settings)
    stats.filter(season_type=self.season_type, season_year=self.season_year, 
      week=self.week)
    stats = stats.get(as_list=False)
    league_scores = []
    for username in self.league.get_members():
      user_score = {'user': username, 'total': 0, 'player_scores': []}
      self.member = models.Member.objects.get(league=self.league, 
        user__username=username)
      for player in self.member.get_lineup(self.season_type, self.season_year, 
        self.week):
        if player['id'] in stats:
          player_stats = stats[player['id']]
        else:
          player_stats = {'player_id': player['id'], 'name': player['name'], 
          'team': player['team'], 'position': player['position'], 'total': 0}  
        user_score['player_scores'].append(player_stats)
        user_score['total'] += player_stats['total']
      # fix some weirdness with floating point addition
      user_score['total'] = round(user_score['total'], 2)
      league_scores.append(user_score)
    reverse_sort = True
    if 'sort' in self.request.GET and self.request.GET['sort'] == 'asc':
      reverse_sort = False
    league_scores.sort(key=lambda user_score: user_score['total'], 
      reverse=reverse_sort)
    self.add_response_data('league_scores', league_scores)
    return self.return_json()