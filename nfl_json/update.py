import argparse

from download import Download

def main():
  parser = argparse.ArgumentParser(description='Download new JSON game data from NFL.com')
  parser.add_argument('--year', type=int, default=None, 
    help='Filter to a specific year.')
  parser.add_argument('--players', action='store_true', 
    help='Force an update on the players JSON file.')
  args = parser.parse_args()
  
  download = Download()
  download.main(year=args.year, force_players_update=args.players)

if __name__ == '__main__':
  main()