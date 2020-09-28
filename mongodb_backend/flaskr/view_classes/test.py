from mongoengine import connect

from mongodb_backend.flaskr.view_classes.stat_query import StatQuery
from mongodb_backend.flaskr.config import SETTINGS

def main():
  connect(SETTINGS['MONGODB_SETTINGS']['db'], 
    host=SETTINGS['MONGODB_SETTINGS']['host'], 
    port=SETTINGS['MONGODB_SETTINGS']['port'], 
    username=SETTINGS['MONGODB_SETTINGS']['username'], 
    password=SETTINGS['MONGODB_SETTINGS']['password'])

  scoring_settings = [
    {'name': 'passing yards', 'field': 'passing_yds', 'conditions': [], 'multiplier': .04},
    {'name': 'passing TDs', 'field': 'passing_tds', 'conditions': [], 'multiplier': 4},
    {'name': 'passing 2pts', 'field': 'passing_twoptm', 'conditions': [], 'multiplier': 2},
    {'name': 'rushing yards', 'field': 'rushing_yds', 'conditions': [], 'multiplier': .1},
    {'name': 'rushing TDs', 'field': 'rushing_tds', 'conditions': [], 'multiplier': 6},
    {'name': 'rushing 2pts', 'field': 'rushing_twoptm', 'conditions': [], 'multiplier': 2},
    {'name': 'receiving yards', 'field': 'receiving_yds', 'conditions': [], 'multiplier': .1},
    {'name': 'receiving TDs', 'field': 'receiving_tds', 'conditions': [], 'multiplier': 6},
    {'name': 'receiving 2pts', 'field': 'receiving_twoptm', 'conditions': [], 'multiplier': 2},
    {'name': 'field goals made', 'field': 'kicking_fgm', 'conditions': [], 'multiplier': 3},
    {'name': 'extra points made', 'field': 'kicking_xpmade', 'conditions': [], 'multiplier': 1},
    {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
    {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 40}, 
    {'field': 'kicking_fgm_yds', 'comparison': '<', 'value': 50}], 'multiplier': 1},
    {'name': 'fg made 40-49 yards', 'field': 'kicking_fgm', 'conditions': [
    {'field': 'kicking_fgm_yds', 'comparison': '>=', 'value': 50}], 'multiplier': 2}]
  stat_query = StatQuery(scoring_settings, 2019, 'REG', 17)
  print(stat_query.get())

if __name__ == '__main__':
  main()