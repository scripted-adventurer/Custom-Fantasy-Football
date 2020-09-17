# -*- coding: utf-8 -*-
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

import datetime
import pytz

def get_current_week():
  now = datetime.datetime.now(pytz.UTC)

  season_year = now.year
  if now.month is 1 or now.month is 2:
    season_year -= 1

  labor_day = datetime.datetime(season_year,9,1,tzinfo=pytz.utc)
  while labor_day.weekday() != 0:  # 0 is monday
    labor_day += datetime.timedelta(days=1)

  regular_season_switch = labor_day + datetime.timedelta(days=2)
  postseason_switch = regular_season_switch + datetime.timedelta(weeks=17)

  # If negative (e.g. preseason), negative integer division will take
  # us "too far" from the switch. This is adjusted later.
  weeks_from_rs_switch = (now - regular_season_switch).days // 7

  if now < regular_season_switch:
    season_type = 'PRE'
    # 5 instead of 4 to adjust for negative integer division
    week = 5 + weeks_from_rs_switch

    if week < 0:
      week = 0

  elif now < postseason_switch:
    season_type = 'REG'
    week = weeks_from_rs_switch + 1

  else:
    season_type = 'POST'
    week = weeks_from_rs_switch - 16

    if week > 4:
      week = 4

  return (season_year, season_type, week)