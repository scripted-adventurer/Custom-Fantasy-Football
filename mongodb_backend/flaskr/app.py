# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_security import Security, login_required
from flask_login import current_user
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface

import os

from . import config
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

def create_app(testing=False):

  app = Flask(__name__)
  for name, value in config.SETTINGS.items():
    app.config[name] = value
  if testing:
    app.config['MONGODB_SETTINGS']['db'] = 'test'
    app.config['TESTING'] = True
    app.config['BCRYPT_LOG_ROUNDS'] = 4
  db = MongoEngine(app)
  app.session_interface = MongoEngineSessionInterface(db)

  @login_required
  @app.route('/games', methods=['GET'])
  def games():
    return Games(request).get()

  @login_required
  @app.route('/league/<league_name>/member', methods=['GET', 'DELETE'])
  def league_member(league_name):
    if request.method == 'GET':
      return LeagueMember(request, current_user, league_name).get()
    elif request.method == 'DELETE':  
      return LeagueMember(request, current_user, league_name).delete()  

  @login_required
  @app.route('/league/<league_name>/member/lineup', methods=['GET', 'PUT'])
  def league_member_lineup(league_name):
    if request.method == 'GET':
      return LeagueMemberLineup(request, current_user, league_name).get()
    elif request.method == 'PUT':  
      return LeagueMemberLineup(request, current_user, league_name).put()

  @login_required
  @app.route('/league/<league_name>/members', methods=['POST'])
  def league_members(league_name):
    return LeagueMembers(request, current_user, league_name).post()

  @login_required
  @app.route('/league/<league_name>/scores', methods=['GET'])
  def league_scores(league_name):
    return LeagueScores(request, current_user, league_name).get()

  @login_required
  @app.route('/league/<league_name>/stats', methods=['GET'])
  def league_stats(league_name):
    return LeagueStats(request, current_user, league_name).get()

  @login_required
  @app.route('/league/<league_name>', methods=['GET', 'PATCH'])
  def league(league_name):
    if request.method == 'GET':
      return League(request, current_user, league_name).get()
    elif request.method == 'PATCH':
      return League(request, current_user, league_name).patch()    

  @login_required
  @app.route('/leagues', methods=['POST'])
  def leagues():
    return Leagues(request, current_user).post() 

  @login_required
  @app.route('/player', methods=['GET'])
  def player():
    return Player(request, current_user).get()

  @login_required
  @app.route('/players', methods=['GET'])
  def players():
    return Players(request, current_user).get()  

  @app.route('/session', methods=['POST', 'DELETE'])
  def session():
    if request.method == 'POST':
      return Session(request).post()
    elif request.method == 'DELETE':
      return Session(request).delete()

  @login_required
  @app.route('/team', methods=['GET'])
  def team():
    return Team(request, current_user).get()

  @login_required
  @app.route('/teams', methods=['GET'])
  def teams():
    return Teams(request, current_user).get()    

  @login_required
  @app.route('/user', methods=['GET', 'DELETE', 'PATCH'])
  def user():
    if request.method == 'GET':
      return User(request, current_user).get()
    elif request.method == 'DELETE':
      return User(request, current_user).delete()
    elif request.method == 'PATCH':
      return User(request, current_user).patch()

  @app.route('/users', methods=['POST'])
  def users():
    return Users(request).post()

  @login_required
  @app.route('/week', methods=['GET'])
  def week():
    return Week(request, current_user).get()

  return app  