import os

DATABASES = {
  'default': {
    'host': os.environ['NFL_MDB_HOST'],   # default is 'localhost',
    'port': int(os.environ['NFL_MDB_PORT']),   # default is 27017
    'user': os.environ['NFL_MDB_USER'],
    'password': os.environ['NFL_MDB_PASSWORD'],
    'db': os.environ['NFL_MDB_DB']
  },
  'test': {
    'host': os.environ['NFL_MDB_HOST'],   # default is 'localhost',
    'port': int(os.environ['NFL_MDB_PORT']),   # default is 27017
    'user': os.environ['NFL_MDB_USER'],
    'password': os.environ['NFL_MDB_PASSWORD'],
    'db': 'test'
  }
}

'''A 'season' is specified by a year and a phase. For example, 2019 REG refers to
the 2019 regular season. Include below a mapping of years to season phase(s) 
from that year. Anything included will be synced into the database.
PRE - Preseason
REG - Regular season
PRO - Pro Bowl
POST - Postseason '''
INCLUDED_SEASONS = {2019: ['PRE', 'REG', 'PRO', 'POST']}