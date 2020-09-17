# -*- coding: utf-8 -*-
import os

from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render

from data.view_classes.games import Games 
from data.view_classes.league import League 
from data.view_classes.league_member import LeagueMember
from data.view_classes.league_member_lineup import LeagueMemberLineup
from data.view_classes.league_members import LeagueMembers
from data.view_classes.league_scores import LeagueScores 
from data.view_classes.league_stats import LeagueStats
from data.view_classes.leagues import Leagues 
from data.view_classes.player import Player 
from data.view_classes.players import Players 
from data.view_classes.session import Session 
from data.view_classes.team import Team
from data.view_classes.teams import Teams 
from data.view_classes.user import User 
from data.view_classes.users import Users 
from data.view_classes.week import Week
from common.errors import Errors

def games(request):
  view = Games(request, login_required=True)
  return view.router()

def league(request, league_name):
  view = League(request, login_required=True, league_name=league_name)
  return view.router()

def league_member(request, league_name):
  view = LeagueMember(request, login_required=True, league_name=league_name)
  return view.router()

# needed for the PUT case as multiple db calls are made to update the lineup
@transaction.atomic
def league_member_lineup(request, league_name):
  view = LeagueMemberLineup(request, login_required=True, league_name=league_name)
  return view.router() 

def league_members(request, league_name):
  view = LeagueMembers(request, login_required=True, league_name=league_name)
  return view.router()

def league_scores(request, league_name):
  view = LeagueScores(request, login_required=True, league_name=league_name)
  return view.router()

def league_stats(request, league_name):
  view = LeagueStats(request, login_required=True, league_name=league_name)
  return view.router()  

def leagues(request):
  view = Leagues(request, login_required=True)
  return view.router()

def player(request):
  view = Player(request, login_required=True)
  return view.router()

def players(request):
  view = Players(request, login_required=True)
  return view.router()     

def session(request):
  view = Session(request, login_required=False)
  return view.router()

def team(request):
  view = Team(request, login_required=True)
  return view.router()

def teams(request):
  view = Teams(request, login_required=True)
  return view.router()

def user(request):
  view = User(request, login_required=True)
  return view.router()      

def users(request):
  view = Users(request, login_required=False)
  return view.router() 

def week(request):
  view = Week(request, login_required=True)
  return view.router()  

def http_400(request, exception):
  response = {'success': False, 'errors': [Errors().http_400()]}
  return JsonResponse(response, status=400)

def http_401(request, exception):
  response = {'success': False, 'errors': [Errors().http_401()]}
  return JsonResponse(response, status=401)  

def csrf_failure(request, reason=""):
  response = {'success': False, 'errors': [Errors().bad_csrf()]}
  return JsonResponse(response, status=403)

def http_403(request, exception):
  response = {'success': False, 'errors': [Errors().http_403()]}
  return JsonResponse(response, status=403)  

def http_404(request, exception):
  response = {'success': False, 'errors': [Errors().http_404()]}
  return JsonResponse(response, status=404)

def http_405(request, exception):
  response = {'success': False, 'errors': [Errors().http_405()]}
  return JsonResponse(response, status=405)  

def http_500(request):
  response = {'success': False, 'errors': [Errors().http_500()]}
  return JsonResponse(response, status=500)