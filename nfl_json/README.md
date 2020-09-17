# NFL JSON #

Inspired by the [nflgame module](https://github.com/BurntSushi/nflgame) and updated to work with the new NFL.com APIs. 

## About ##

This module syncs JSON data from the NFL.com API to a local folder structure. It comes with all existing data from 2011 through 2019. It can be used for real-time updates, however to sync new data from NFL.com you will need to provide an API key in the 'NFL_API_KEY' environment variable. 

Below is a quick summary of the folder structure:
- **schedule**: Contains metadata on each game in an NFL year, including data for preseason, regular season, postseason, and the Pro Bowl. One file per year. 
- **games**: Contains all data from each game listed in the schedule files (one file per game). This folder is compressed to save space. 
- **currentPlayers.json**: Contains a dictionary of player ID and player data entries for each player currently active in the NFL. This file is overwritten with new data each time players update is run.