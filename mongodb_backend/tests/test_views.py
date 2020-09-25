from freezegun import freeze_time
import os

from flask_login import logout_user

from mongodb_backend.tests.view_test_request import ViewTestRequest
from mongodb_backend.tests.setup import Cases
from mongodb_backend.flaskr import models
from common.hashing import generate_hash, compare_hash

def test_views(client):
  test_cases = Cases().get()
  hashed_password = generate_hash('password')
  users = []
  users.append(models.User(username="test_user_0", password=hashed_password).save())
  users.append(models.User(username="test_user_1", password=hashed_password).save())
  users.append(models.User(username="test_user_2", password=hashed_password).save())
  users.append(models.User(username="test_user_3", password=hashed_password).save())

  def test_games():
    for test in test_cases['games']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

  def test_league():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()
    member_0 = models.Member(user=users[0], league=league_0).save()
    member_1 = models.Member(user=users[1], league=league_0, admin=True).save()

    for test in test_cases['league']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    # check data is updated
    league = models.League.objects.get(name='test_league_0')
    assert (compare_hash(league.password, 'new_password'))

    # reset test data
    models.Member.objects.delete()
    models.League.objects.delete()
 
  def test_league_member():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()
    member_0 = models.Member(user=users[0], league=league_0, admin=True).save()
    member_1 = models.Member(user=users[1], league=league_0).save()
    member_1 = models.Member(user=users[2], league=league_0).save()

    for test in test_cases['league_member']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    # check members are removed
    league = models.League.objects.get(name='test_league_0')
    assert league.get_members() == ['test_user_0']

    models.Member.objects.delete()
    models.League.objects.delete()

  # Sunday 2PM during Week 17 2019 (1PM players are locked, others available)
  @freeze_time("2019-12-29 19:00:00")
  def test_league_member_lineup():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()
    league_0.set_lineup_settings({'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2})
    member_0 = models.Member(user=users[0], league=league_0).save()
    member_1 = models.Member(user=users[1], league=league_0).save()
    # Travis Kelce ('32004b45-4c01-2458-b7b6-3a14cdb414dd') is locked here 
    lineup = ['32005455-4322-4643-f70e-a24b7ce9db07', 
      '32005745-4e61-5770-9c68-1652f876bc72', '32004241-5219-2674-af43-1519254e563d', 
      '3200454c-4c28-9284-cdcc-74694c8d1749', '32004b45-4c01-2458-b7b6-3a14cdb414dd', 
      '32005748-4972-2063-1ea8-adb8ac89fa9d', '32004b55-5053-4597-b958-87408c31956f']
    
    member_1.lineup_add(lineup, 'REG', 2019, 17)

    for test in test_cases['league_member_lineup']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    models.Member.objects.delete()
    models.League.objects.delete()  

  def test_league_members():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()

    for test in test_cases['league_members']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    models.Member.objects.delete()
    models.League.objects.delete()  

  def test_league_stats_scores():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()
    lineup_settings = {'K': 1, 'QB': 1, 'RB': 2, 'TE': 1, 'WR': 2}
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
    league_0.set_lineup_settings(lineup_settings)
    league_0.set_scoring_settings(scoring_settings)
    member_0 = models.Member(user=users[0], league=league_0).save()
    member_1 = models.Member(user=users[1], league=league_0).save()
    lineup = ['3200524f-4433-9293-a3cf-ad7758d03003', 
      '32004a4f-4e02-6624-33bd-3ba151b7013d', '32004241-5219-2674-af43-1519254e563d', 
      '32004144-4121-8591-4d26-4c0ac739af41', '32004144-4121-8591-4d26-4c0ac739af41', 
      '32004552-5480-0920-32a6-165b5a77814e', '32004352-4f36-9933-a863-d4bf2cc5772e']
    member_1.lineup_add(lineup, 'REG', 2019, 17)
    lineup = ['3200424c-4f31-5389-8dc7-e49c9f486370', 
      '32004a4f-4839-9188-cb7b-f29b5ea64839', '3200454c-4c28-9284-cdcc-74694c8d1749', 
      '3200474f-4c57-3546-c21d-b780be32aca0', '3200434f-4f29-9382-29e1-70020b0a09be', 
      '32004b45-4c01-2458-b7b6-3a14cdb414dd', '32005052-4114-3616-ccef-0127103fb075']
    member_0.lineup_add(lineup, 'REG', 2019, 17)

    for test in test_cases['league_stats']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    for test in test_cases['league_scores']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    models.Member.objects.delete()
    models.League.objects.delete()  

  def test_leagues():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()

    for test in test_cases['leagues']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

    # check data is created
    league = models.League.objects.get(name='new_league')
    member = models.Member.objects.get(user=users[0], league=league)
    assert member.admin

    models.Member.objects.delete()
    models.League.objects.delete() 

  def test_player():
    for test in test_cases['player']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

  # Sunday afternoon during Week 17 2019
  @freeze_time("2019-12-29 18:30:00")
  def test_players():
    for test in test_cases['players']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()   

  def test_session():
    for test in test_cases['session']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()   

  def test_team():
    for test in test_cases['team']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run() 

  def test_teams():
    for test in test_cases['teams']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run() 

  def test_user():
    league_0 = models.League(name='test_league_0', password=hashed_password).save()
    league_1 = models.League(name='test_league_1', password=hashed_password).save()
    member_0 = models.Member(user=users[1], league=league_0).save()
    member_1 = models.Member(user=users[1], league=league_1).save()

    for test in test_cases['user']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run() 
    
    # check data was updated
    user_1 = models.User.objects(username=users[1].username)
    assert not len(user_1)

    models.Member.objects.delete()
    models.League.objects.delete() 

  def test_users():
    for test in test_cases['users']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run() 

    # check data is created
    user1 = models.User.objects.get(username='test_new_user')
    user2 = models.User.objects.get(username='test_new_user_2')
    # logout the newly created user
    client.delete('/api/session', json={})

  def test_week():
    for test in test_cases['week']:
      test_case = ViewTestRequest(client, test.test_case, test.test_id, test.url, 
        test.method, test.request, test.username, test.status_code, 
        test.full_response, test.json_expression, test.parsed_response)
      assert test_case.run()

  test_games()
  test_league()
  test_league_member()
  test_league_member_lineup()
  test_league_members()
  # test_league_stats_scores()
  test_leagues()
  test_player()
  test_players()
  test_session()
  test_team()
  test_teams()
  test_user()
  test_users()
  test_week()  