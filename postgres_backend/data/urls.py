from django.conf.urls import url
from . import views

app_name = 'api'
urlpatterns = [
  url(r'^games$', views.games, name='games'),
  url(r'^league/(?P<league_name>.+)/member$', views.league_member, 
    name='league_member'),
  url(r'^league/(?P<league_name>.+)/member/lineup$', views.league_member_lineup, 
    name='league_member_lineup'),
  url(r'^league/(?P<league_name>.+)/members$', views.league_members, 
    name='league_members'),
  url(r'^league/(?P<league_name>.+)/scores$', views.league_scores, 
    name='league_scores'),
  url(r'^league/(?P<league_name>.+)/stats$', views.league_stats, 
    name='league_stats'),
  url(r'^league/(?P<league_name>.+)$', views.league, name='league'),
  url(r'^leagues$', views.leagues, name='leagues'),
  url(r'^player$', views.player, name='player'),
  url(r'^players$', views.players, name='players'),
  url(r'^session$', views.session, name='session'),
  url(r'^team$', views.team, name='team'),
  url(r'^teams$', views.teams, name='teams'),
  url(r'^user$', views.user, name='user'),
  url(r'^users$', views.users, name='users'),
  url(r'^week$', views.week, name='week')
]