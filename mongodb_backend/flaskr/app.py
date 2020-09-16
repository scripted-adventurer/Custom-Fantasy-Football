# -*- coding: utf-8 -*-
from flask import Flask, request, json, Response
from flask_login import LoginManager, login_required, current_user
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface

import os

from . import config
from . import security
from .view_classes.games import Games 
from .view_classes.league import League 
from .view_classes.league_member import LeagueMember
from .view_classes.league_member_lineup import LeagueMemberLineup
from .view_classes.league_members import LeagueMembers
from .view_classes.league_scores import LeagueScores 
from .view_classes.league_stats import LeagueStats
from .view_classes.leagues import Leagues 
from .view_classes.player import Player 
from .view_classes.players import Players 
from .view_classes.session import Session 
from .view_classes.team import Team
from .view_classes.teams import Teams 
from .view_classes.user import User 
from .view_classes.users import Users 
from .view_classes.week import Week

import importlib.util
spec = importlib.util.spec_from_file_location("common", 
  f"{os.environ['CUSTOM_FF_PATH']}/common/common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
Errors = common.Errors

def create_app(testing=False):

  app = Flask(__name__)
  for name, value in config.SETTINGS.items():
    app.config[name] = value
  if testing:
    app.config['MONGODB_SETTINGS']['db'] = 'test'
    app.config['TESTING'] = True
    app.config['BCRYPT_LOG_ROUNDS'] = 4
  db = MongoEngine(app)
  login_manager = LoginManager()
  login_manager.init_app(app)
  app.session_interface = MongoEngineSessionInterface(db)

  @login_manager.user_loader
  def load_user(user_id):
    return security.User.objects(id=user_id).first()  

  @app.route('/api/games', methods=['GET'])
  @login_required
  def games():
    return Games(request).get()

  @app.route('/api/league/<league_name>/member', methods=['GET', 'DELETE'])
  @login_required
  def league_member(league_name):
    if request.method == 'GET' or request.method == 'HEAD':
      return LeagueMember(request, current_user, league_name).get()
    elif request.method == 'DELETE':  
      return LeagueMember(request, current_user, league_name).delete()  

  @app.route('/api/league/<league_name>/member/lineup', methods=['GET', 'PUT'])
  @login_required
  def league_member_lineup(league_name):
    if request.method == 'GET' or request.method == 'HEAD':
      return LeagueMemberLineup(request, current_user, league_name).get()
    elif request.method == 'PUT':  
      return LeagueMemberLineup(request, current_user, league_name).put()

  @app.route('/api/league/<league_name>/members', methods=['POST'])
  @login_required
  def league_members(league_name):
    return LeagueMembers(request, current_user, league_name).post()

  @app.route('/api/league/<league_name>/scores', methods=['GET'])
  @login_required
  def league_scores(league_name):
    return LeagueScores(request, current_user, league_name).get()

  @app.route('/api/league/<league_name>/stats', methods=['GET'])
  @login_required
  def league_stats(league_name):
    return LeagueStats(request, current_user, league_name).get()

  @app.route('/api/league/<league_name>', methods=['GET', 'PATCH'])
  @login_required
  def league(league_name):
    if request.method == 'GET' or request.method == 'HEAD':
      return League(request, current_user, league_name).get()
    elif request.method == 'PATCH':
      return League(request, current_user, league_name).patch()    

  @app.route('/api/leagues', methods=['POST'])
  @login_required
  def leagues():
    return Leagues(request, current_user).post() 

  @app.route('/api/player', methods=['GET'])
  @login_required
  def player():
    return Player(request, current_user).get()

  @app.route('/api/players', methods=['GET'])
  @login_required
  def players():
    return Players(request, current_user).get()  

  @app.route('/api/session', methods=['POST', 'DELETE'])
  def session():
    if request.method == 'POST':
      return Session(request).post()
    elif request.method == 'DELETE':
      return Session(request).delete()

  @app.route('/api/team', methods=['GET'])
  @login_required
  def team():
    return Team(request, current_user).get()

  @app.route('/api/teams', methods=['GET'])
  @login_required
  def teams():
    return Teams(request, current_user).get()    

  @app.route('/api/user', methods=['GET', 'DELETE', 'PATCH'])
  @login_required
  def user():
    if request.method == 'GET' or request.method == 'HEAD':
      return User(request, current_user).get()
    elif request.method == 'DELETE':
      return User(request, current_user).delete()
    elif request.method == 'PATCH':
      return User(request, current_user).patch()

  @app.route('/api/users', methods=['POST'])
  def users():
    return Users(request).post()

  @app.route('/api/week', methods=['GET'])
  @login_required
  def week():
    return Week(request, current_user).get()

  @app.errorhandler(400)
  def bad_request(e):
    response = {'success': False, 'errors': [Errors().http_400()]}
    return Response(json.dumps(response), status=400, mimetype='application/json')  

  @app.errorhandler(401)
  def unauthorized(e):
    response = {'success': False, 'errors': [Errors().http_401()]}
    return Response(json.dumps(response), status=401, mimetype='application/json')

  @app.errorhandler(403)
  def forbidden(e):
    response = {'success': False, 'errors': [Errors().http_403()]}
    return Response(json.dumps(response), status=403, mimetype='application/json')

  @app.errorhandler(404)
  def page_not_found(e):
    response = {'success': False, 'errors': [Errors().http_404()]}
    return Response(json.dumps(response), status=404, mimetype='application/json')

  @app.errorhandler(405)
  def method_not_allowed(e):
    response = {'success': False, 'errors': [Errors().http_405()]}
    return Response(json.dumps(response), status=405, mimetype='application/json')

  @app.errorhandler(500)
  def server_error(e):
    response = {'success': False, 'errors': [Errors().http_500()]}
    return Response(json.dumps(response), status=500, mimetype='application/json')  

  return app  