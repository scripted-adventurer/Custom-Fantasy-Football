# -*- coding: utf-8 -*-
import os

SETTINGS = {
  'SECRET_KEY': os.environ['SECRET_KEY'],
  'MONGODB_SETTINGS': {
    'db': os.environ['NFL_MDB_DB'],
    'host': os.environ['NFL_MDB_HOST'],
    'port': int(os.environ['NFL_MDB_PORT']),
    'username': os.environ['NFL_MDB_USER'],
    'password': os.environ['NFL_MDB_PASSWORD']
  }
}

'''A 'season' is specified by a year and a phase. For example, 2019 REG refers to
the 2019 regular season. Include below a mapping of years to season phase(s) 
from that year. Anything included will be synced into the database.
PRE - Preseason
REG - Regular season
PRO - Pro Bowl
POST - Postseason '''
INCLUDED_SEASONS = {
  2020: ['PRE', 'REG', 'PRO', 'POST'],
  2019: ['PRE', 'REG', 'PRO', 'POST']
}