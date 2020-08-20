# Custom Fantasy Football #

A modular web application that creates a platform for fully customized fantasy football leagues. 

## About ##

Ever felt like the reason you can't win your fantasy football league is because the rules are too vanilla and you aren't able to manipulate them fully to your advantage? Using this API, you can create leagues with any number of users, any combination of lineup positions (including defensive players) and any scoring settings (including stats like rushing yards, passing first downs, 40-49 yard field goals made, and everything in between). 

## Components ##

- nfl_json: Syncs data between the NFL.com API and locally stored JSON files
- mongodb_backend: One of two backend options for the application. Syncs stats data from the JSON files into MongoDB and provides methods to implement all the API requests.
- postgres_backend: One of two backend options for the application. Syncs stats data from the JSON files into a Postgres db and provides methods to implement all the API requests (using Django).
- api: The Flask module that powers the API requests. Uses either mongodb_backend or postgres_backend, depending on which is configured. 
- frontend: A React single page application that provides all UI functionality. 

The below subheadings explain the various components of the application.

### Users ###

User authentication follows standard password authentication. Usernames must be globally unique throughout the application. Each user can be in multiple leagues, and each league can have multiple associated users. 

### Leagues ###

Each league has a password (stored in hashed form), associated members (users who are part of that league, including an administrator), lineup settings, and scoring settings. Users join the league by providing the correct password. The league administrator is responsible for defining all the league' settings, and can also remove users from the league. 

### Lineup Settings ###

Each league's lineup settings define the number and type of position groups used in lineups submitted for that league. For example, a "standard" league lineup might consist of 1 quarterback, 2 running backs, 2 wide receivers, 1 tight end, and 1 kicker. In the JSON format used by the API, this would be: 

```
{"K":1, "QB":1, "RB":2, "TE":1, "WR":2}
```

In addition to standard offensive skill players, offensive lineman, defensive players, and punters are also supported. The full breakdown is below:

- Defensive backs (DB) - includes positions CB, DB, FS, SAF, SS
- Defensive lineman (DL) - includes positions DE, DT, NT
- Kickers (K) - includes position K
- Linebackers (LB) - includes positions ILB, LB, MLB, OLB
- Offensive lineman (OL) - includes positions C, LS, OG, OT
- Punters (P) - includes position P
- Quarterbacks (QB) - includes position QB
- Running backs (RB) - includes positions FB, RB
- Tight ends (TE) - includes position TE
- Wide receivers (WR) - includes position WR

### Scoring Settings ###

Each league's scoring settings are made up of a collection of user defined stats. Each stat maps to a particular stat name from the data model (like rushing_yds), which is used as the value of that stat. Each stat also contains a multiplier, which is used in calculating point totals. Finally, each stat also contains an optional number of conditions, which provide complete flexibility to create a wide array of custom stats. 

Conditions are user defined booleans, which all must be true for the stat to count. For example, say you wanted to award bonus points for passing plays of 25 or more yards. This is simple to construct in the application:
1. Create a stat called '25+ yard completions'.
2. Map it to the passing_cmp category of the data model.
3. Provide a condition that the passing_yds category must be greater than or equal to 25.

In the JSON format used by the API, this stat would look like this: 

```
{"name":"25+ yard completions", "stat":"passing_cmp", "conditions":
[{stat":"passing_yds", "comparison":">=", "value":25}], "multiplier":1}
```

When you request stats info from the API, the engine will search the database for plays where play_player passing_yds was greater than or equal to 25, and provide for each player a sum of the associated play_player passing_cmp values for all matching rows. The associated SQL query executed on the backend would look something like this:

```
SELECT SUM(play_player.passing_cmp)
FROM play_player
WHERE play_player.passing_yds >= 25
```

In this example, the passing_cmp value is always either 0 or 1 based on whether or not a completion occurred. This means the sum will be a simple count of matching rows. By providing a different column to map as the stat's value, however, you could create even more complex stats like total passing yards from all plays of at least 25 passing yards.

The point total for each player is calculated by taking the sum of each stat's value multiplied by its multiplier. For example, given the below stats and multipliers:

Pass yards    .04<br>
Pass TDs        6<br>
Rush/rec yards .1<br>
Rush/rec TDs    6

And the below stat line:

Pass yards    323<br>
Pass TDs        2<br>
Rush yards      1

The total for the player would be 21.02. 

### Players ###

User lineups consist of players pulled from the players data model. The application operates in a manner similar to daily fantasy football where user player selections can overlap and individual players are not "owned".

Users are allowed to edit their lineups for a given week at any time, however lineups are restricted through the use of player locking logic. After a player's game for the week starts, that player is "locked". When submitting a new lineup, users cannot remove existing players who are locked and also cannot add new players who are locked. This system prevents users from setting their lineups based on how players already performed during the week, which obviously is necessary for a fair league. 


## Stat Guide ##

Below is a guide to the player stats stored in the data model. These categories are the same ones used in the nflgame module and are defined in the statmap.py file (copied from that project).
- defense_ast   Assist to a tackle.
- defense_ffum  Defensive player forced a fumble.
- defense_fgblk   Defensive player blocked a field goal.
- defense_frec  Defensive player recovered a fumble by the opposing team.
- defense_frec_tds  Defensive player scored a touchdown after recovering a fumble by the opposing team.
- defense_frec_yds  Yards gained by a defensive player after recovering a fumble by the opposing team.
- defense_int   An interception.
- defense_int_tds   A touchdown scored after an interception.
- defense_int_yds   Yards gained after an interception.
- defense_misc_tds  A touchdown scored on miscellaneous yardage (e.g., on a missed field goal or a blocked punt).
- defense_misc_yds  Miscellaneous yards gained by a defensive player (e.g., yardage on a missed field goal or blocked punt).
- defense_pass_def  Incomplete pass was due primarily to a defensive player's action.
- defense_puntblk   Defensive player blocked a punt.
- defense_qbhit   Defensive player knocked the quarterback to the ground and the quarterback was not the ball carrier.
- defense_safe  Tackle by a defensive player that resulted in a safety. This is in addition to a tackle.
- defense_sk  Defensive player sacked the quarterback. Note that this is the only field that is a floating point number. Namely, there can be half-credit sacks.
- defense_sk_yds  Yards lost as a result of a sack.
- defense_tkl   A defensive player tackle. (This include defense_tkl_primary.)
- defense_tkl_loss  Defensive player tackled the runner behind the line of scrimmage. Play must have ended, player must have received a tackle stat, has to be an offensive player tackled.
- defense_tkl_loss_yds  The number of yards lost caused by a defensive tackle behind the line of scrimmage.
- defense_tkl_primary   Defensive player was the primary tackler.
- defense_xpblk   Defensive player blocked the extra point.
- fumbles_forced  Player fumbled the ball, fumble was forced by another player.
- fumbles_lost  Player fumbled the ball and the opposing team recovered it.
- fumbles_notforced   Player fumbled the ball that was not caused by a defensive player.
- fumbles_oob   Player fumbled the ball, and the ball went out of bounds.
- fumbles_rec   Fumble recovery from a player on the same team.
- fumbles_rec_tds   A touchdown after a fumble recovery from a player on the same team.
- fumbles_rec_yds   Yards gained after a fumble recovery from a player on the same team.
- fumbles_tot   Total number of fumbles by a player. Includes forced, not forced and out-of-bounds.
- kicking_all_yds   Kickoff and length of kick. Includes end zone yards for all kicks into the end zone, including kickoffs ending in a touchback.
- kicking_downed  A downed kickoff. A kickoff is downed when touched by an offensive player within the 10 yard free zone, and the ball is awarded to the receivers at the spot of the touch.
- kicking_fga   A field goal attempt, including blocked field goals. Unlike a punt, a field goal is statistically blocked even if the ball does go beyond the line of scrimmage.
- kicking_fgb   Field goal was blocked. Unlike a punt, a field goal is statistically blocked even if the ball does go beyond the line of scrimmage.
- kicking_fgm   A field goal.
- kicking_fgm_yds   The length of a successful field goal.
- kicking_fgmissed  The field goal was unsuccessful, including blocked field goals. Unlike a punt, a field goal is statistically blocked even if the ball does go beyond the line of scrimmage.
- kicking_fgmissed_yds  The length of an unsuccessful field goal, including blocked field goals. Unlike a punt, a field goal is statistically blocked even if the ball does go beyond the line of scrimmage.
- kicking_i20   Kickoff and length of kick, where return ended inside opponent's 20 yard line.
- kicking_rec   Recovery of own kickoff, whether or not the kickoff is onside.
- kicking_rec_tds   Touchdown resulting from direct recovery in endzone of own kickoff, whether or not the kickoff is onside.
- kicking_tot   A kickoff.
- kicking_touchback   A kickoff that resulted in a touchback.
- kicking_xpa   An extra point attempt.
- kicking_xpb   Extra point was blocked.
- kicking_xpmade  Extra point good.
- kicking_xpmissed  Extra point missed. This includes blocked extra points.
- kicking_yds   The length of a kickoff.
- kickret_fair  A fair catch kickoff return.
- kickret_oob   Kicked ball went out of bounds.
- kickret_ret   A kickoff return.
- kickret_tds   A kickoff return touchdown.
- kickret_touchback   A kickoff return that resulted in a touchback.
- kickret_yds   Yards gained by a kickoff return.
- passing_att   A pass attempt.
- passing_cmp   A pass completion.
- passing_cmp_air_yds   Length of a pass, not including the yards gained by the receiver after the catch.
- passing_incmp   Pass was incomplete.
- passing_incmp_air_yds   Length of the pass, if it would have been a completion.
- passing_int   Pass attempt that resulted in an interception.
- passing_sk  The player was sacked.
- passing_sk_yds  The yards lost by a player that was sacked.
- passing_tds   A pass completion that resulted in a touchdown.
- passing_twopta  A passing two-point conversion attempt.
- passing_twoptm  A successful passing two-point conversion.
- passing_twoptmissed   An unsuccessful passing two-point conversion.
- passing_yds   Total yards resulting from a pass completion.
- punting_blk   Punt was blocked. A blocked punt is a punt that is touched behind the line of scrimmage, and is recovered, or goes out of bounds, behind the line of scrimmage. If the impetus of the punt takes it beyond the line of scrimmage, it is not a blocked punt.
- punting_i20   A punt where the punt return ended inside the opponent's 20 yard line.
- punting_tot   A punt.
- punting_touchback   A punt that results in a touchback.
- punting_yds   The length of a punt.
- puntret_downed  Punt return where the ball was downed by kicking team.
- puntret_fair  Punt return resulted in a fair catch.
- puntret_oob   Punt went out of bounds.
- puntret_tds   A punt return touchdown.
- puntret_tot   A punt return.
- puntret_touchback   A punt return that resulted in a touchback.
- puntret_yds   Yards gained by a punt return.
- receiving_rec   A reception.
- receiving_tar   Player was the target of a pass attempt.
- receiving_tds   A reception that results in a touchdown.
- receiving_twopta  A receiving two-point conversion attempt.
- receiving_twoptm  A successful receiving two-point conversion.
- receiving_twoptmissed   An unsuccessful receiving two-point conversion.
- receiving_yac_yds   Yardage from where the ball was caught until the player's action was over.
- receiving_yds   Yards resulting from a reception.
- rushing_att   A rushing attempt.
- rushing_loss  Ball carrier was tackled for a loss behind the line of scrimmage, where at least one defensive player is credited with ending the rush with a tackle, or tackle assist.
- rushing_loss_yds  Yards lost from the ball carrier being tackled for a loss behind the line of scrimmage, where at least one defensive player is credited with ending the rush with a tackle, or tackle assist.
- rushing_tds   A touchdown resulting from a rush attempt.
- rushing_twopta  A rushing two-point conversion attempt.
- rushing_twoptm  A successful rushing two-point conversion.
- rushing_twoptmissed   An unsuccessful rushing two-point conversion.
- rushing_yds   Yards resulting from a rush.

## API Guide ##

**URI:** /api/session<br>
**Method:** POST<br>
**Sample request:**
```
{
  "username": "Spider_2Y_Banana",
  "password": "O9II4AMzPDGEYQHXYCZf"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Creates a new session by logging the requested user into the application.<br>
**Requirements:** Username and password must be correct.
<br><br>

**URI:** /api/session<br>
**Method:** DELETE<br>
**Sample request:**
```
{}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Tears down a session by logging out the requesting user.<br>
**Requirements:** None
<br><br>

**URI:** /api/users<br>
**Method:** POST<br>
**Sample request:**
```
{
  "username": "Spider_2Y_Banana",
  "password1": "O9II4AMzPDGEYQHXYCZf",
  "password2": "O9II4AMzPDGEYQHXYCZf"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Creates a new user for the application.<br>
**Requirements:** Username must be unique. <br>
Passwords must match.
<br><br>

**URI:** /api/user<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "username": "Spider_2Y_Banana",
  "leagues": [
    "SeanMcVaysCoachingTree",
    "UniversityOfPhoenixAlumni2016",
    "EsperantoSpeakersWorldwide"
  ]
}
```
**Description:** Retrieves information about the requesting user. Currently, this is the username and a list of league names that the user is a member of.<br>
**Requirements:** None
<br><br>

**URI:** /api/user<br>
**Method:** DELETE<br>
**Sample request:**
```
{
  "password": "O9II4AMzPDGEYQHXYCZf"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Deletes the requesting user's account.<br>
**Requirements:** Password must be valid (this request requires re-authentication for security).
<br><br>

**URI:** /api/user<br>
**Method:** PATCH<br>
**Action:** Change password<br>
**Sample request:**
```
{
  "property": "password",
  "data": {
    "old_password": "O9II4AMzPDGEYQHXYCZf",
    "new_password1": "RQ4oDo5f64UgHE9Lhv02",
    "new_password2": "RQ4oDo5f64UgHE9Lhv02"
  }
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Updates the user’s password<br>
**Requirements:** Old password must be valid (this request requires re-authentication for security).
<br><br>

**URI:** /api/leagues<br>
**Method:** POST<br>
**Sample request:**
```
{
  "new_league_name": "SeanMcVaysCoachingTree",
  "password1": "LARams4Lyfe",
  "password2": "LARams4Lyfe"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Creates a new league. Makes the requesting user the admin of the league.<br> 
**Requirements:** League name must not already be taken.<br>
Passwords must match.
<br><br>

**URI:** /api/league/{league_name}<br>
**Method:** GET<br>
**Sample response:** 
```
{
  "success": true,
  "members": [
    "Brandon_Butterfingers_Bostick",
    "Alouettes_Legend_Johnny_Football",
    "MrBigChest"
  ],
  "lineup_settings": {
    "K": 1,
    "QB": 1,
    "RB": 2,
    "TE": 1,
    "WR": 2
  },
  "scoring_settings": [
    {
      "name": "passing yards",
      "stat": "passing_yds",
      "conditions": [],
      "multiplier": 0.04
    },
    {
      "name": "passing TDs",
      "stat": "passing_tds",
      "conditions": [],
      "multiplier": 4
    }
  ]
}
```
**Description:** Retrieves current information about the league, including a list of members, lineup settings, and scoring settings.<br>
**Requirements:** Requesting user must be a member of the league.
<br><br>

**URI:** /api/league/{league_name}<br>
**Method:** PATCH<br>
**Action:** Change password<br>
**Sample request:**
```
{
  "property": "password",
  "data": {
    "password1": "aJaredGoffsunrise",
    "password2": "aJaredGoffsunrise"
  }
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Updates the league's password.<br>
**Requirements:** Requesting user must be the admin of the league. 
Passwords must match.<br>
<br><br>

**URI:** /api/league/{league_name}<br>
**Method:** PATCH<br>
**Action:** Change lineup settings<br>
**Sample request:**
```
{
  "property": "lineup_settings",
  "data": {
    "QB": 1,
    "RB": 2,
    "WR": 2,
    "TE": 1,
    "K": 1
  }
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Updates the number of each position group present in a lineup for the league. User submitted lineups will be validated against this setting to ensure they have the correct number of players at each position group. <br>
**Requirements:** Position group names must be valid. Valid groups are: 'DB', 'DL', 'K', 'LB', 'OL', 'P', 'QB', 'RB', 'TE', 'WR'<br>
Position group values must be valid integers. <br>
Requesting user must be the admin of the league.
<br><br>

**URI:** /api/league/{league_name}<br>
**Method:** PATCH<br>
**Action:** Change scoring settings<br>
**Sample request:**
```
{
  "property": "scoring_settings",
  "data": [
    {
      "name": "passing yards",
      "stat": "passing_yds",
      "conditions": [],
      "multiplier": 0.04
    },
    {
      "name": "passing TDs",
      "stat": "passing_tds",
      "conditions": [],
      "multiplier": 4
    }
  ]
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Updates the scoring settings for the league. Each entry in the 'scoring_settings' list should correspond to one user-defined stat for the league. See the explanation on user-defined stats above for more details. <br>
**Requirements:** Each user-defined stat must be valid.<br>
Requesting user must be the admin of the league.
<br><br>

**URI:** /api/league/{league_name}/scores?seasonType=Regular&seasonYear=2019&week=17&sort=desc<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "league_scores": [
    {
      "user": "test_user_0",
      "total": 67.52,
      "player_scores": [
        {
          "player_id": "00-0020531",
          "name": "Drew Brees",
          "team": "NO",
          "position": "QB",
          "passing yards": 253,
          "passing TDs": 3,
          "rushing yards": -1,
          "total": 22.02
        }
      ]
    }
  ]
}
```
**Description:** Retrieves a list of user score objects for the week, each containing the user's total score as well as detailed information on all the players in the user's lineup.<br>
'seasonType', 'seasonYear', and 'week' are optional URI parameters that retrieve data for a specific week. If not provided, the current week is used.<br>
'sort' is an optional URI parameter specifying the ordering of the league scores - "asc" for ascending and "desc" for descending. If not provided, descending is used.<br>
**Requirements:** Requesting user must be a member of the league.
<br><br>

**URI:** /api/{league_name}/stats?playerId=00-0023459&seasonType=Regular&seasonYear=2019&week=17&sort=desc<br>
**Method:** GET<br>
**Sample responses:**
```
{
  "success": true,
  "stats": [
    {
      "player_id": "00-0023459",
      "name": "Aaron Rodgers",
      "team": "GB",
      "position": "QB",
      "passing yards": 323,
      "passing TDs": 2,
      "rushing yards": 1,
      "total": 21.02
    }
  ]
}
---  
{
  "success": true,
  "stats": [
    {
      "id": "00-0032764",
      "name": "Derrick Henry",
      "team": "TEN",
      "position": "RB",
      "rushing yards": 211,
      "rushing TDs": 3,
      "total": 39.1
    },
    {
      "id": "00-0034414",
      "name": "Boston Scott",
      "team": "PHI",
      "position": "RB",
      "rushing yards": 54,
      "rushing TDs": 3,
      "receiving yards": 84,
      "total": 31.8
    },
    {
      "id": "00-0033077",
      "name": "Dak Prescott",
      "team": "DAL",
      "position": "QB",
      "passing yards": 303,
      "passing TDs": 4,
      "rushing yards": 35,
      "total": 31.62
    }
  ]
}
```
**Description:** Calculates and returns stats for the specified season week according to the scoring settings defined for the league. <br>
'playerId' is an optional parameter that filters the results to one specific player. If not provided, all players are returned.<br>
'seasonType', 'seasonYear', and 'week' are optional parameters that retrieve data for a specific week. If not provided, the current week is used.<br>
'sort' is an optional parameter specifying the ordering of the scores - "asc" for ascending and "desc" for descending. If not provided, the results are returned in arbitrary order.<br>
**Requirements:** Player ID, if present, must be valid.<br>
Requesting user must be a member of the league.<br>
Season type, season year, and week (if specified) must refer to a valid season week.
<br><br>

**URI:** /api/league/{league_name}/members<br>
**Method:** POST<br>
**Sample request:**
```
{
  "password": "LARams4Lyfe"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Creates a new member for the league (by adding the requesting user). <br>
**Requirements:** Password provided must match the league's password.
<br><br>

**URI:** /api/league/{league_name}/member<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "admin": true
}
```
**Description:** Retrieves information about the requesting user’s membership in the specified league, including whether or not they are an admin.<br>
**Requirements:** Requesting user must be a member of the league.
<br><br>

**URI:** /api/league/{league_name}/member<br>
**Method:** DELETE<br>
**Sample request:**
```
{
  "password": "O9II4AMzPDGEYQHXYCZf"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Deletes the requesting user from the specified league.<br>
**Requirements:** Requesting user must be a member of the league.<br>
Password must be valid (this request requires re-authentication for security).
<br><br>

**URI:** /api/league/{league_name}/member<br>
**Method:** DELETE<br>
**Sample request:**
```
{
  "username": "secretChargersfan_99"
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Deletes the user specified by the username from the league.<br> 
**Requirements:** Specified user must be a member of the league. <br>
Requesting user must be the admin of the league.
<br><br>

**URI:** /api/league/{league_name}/member/lineup<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "lineup": [
    {
      "id": "00-0020531",
      "name": "Drew Brees",
      "team": "NO",
      "position": "QB"
    },
    {
      "id": "00-0034844",
      "name": "Saquon Barkley",
      "team": "NYG",
      "position": "RB"
    },
    {
      "id": "00-0027944",
      "name": "Julio Jones",
      "team": "ATL",
      "position": "WR"
    }
  ]
}
```
**Description:** Retrieves the requesting user's current lineup for the league specified.<br>
**Requirements:** Requesting user must be a member of the league.<br>
<br><br>

**URI:** /api/league/{league_name}/member/lineup<br>
**Method:** PUT<br>
**Sample request:**
```
{
  "lineup": [
    "00-0020531",
    "00-0034844",
    "00-0027944"
  ]
}
```
**Sample response:**
```
{
  "success": true
}
```
**Description:** Updates the requesting user's current lineup for the league specified using the player IDs specified in 'lineup'.<br>
**Requirements:** Lineup must be valid (see the explanation above for more details).<br>
Requesting user must be a member of the league.
<br><br>

**URI:** /api/players?query=Aaron+Rogers<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "players": [
    {
      "id": "00-0023459",
      "name": "Aaron Rodgers",
      "team": "GB",
      "pos": "QB",
      "status": "Active",
      "injury_status": "Questionable",
      "news": "Rodgers completed 31 of 39 passes for 326 yards with two touchdowns ..."
    }
  ]
}
```
**Description:** Performs an approximate string search using the player name specified, and returns a list of results ordered by relevance. <br>
**Requirements:** None
<br><br>

**URI:** /api/players?available=true<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "players": {
    "DB": [
      {
        "id": "00-0031404",
        "name": "Adrian Phillips",
        "team": "LAC",
        "position": "DB",
        "status": "Active",
        "injury_status": "None",
        "news": "None"
      },
      {
        "id": "00-0034594",
        "name": "A.J. Moore",
        "team": "HOU",
        "position": "DB",
        "status": "Active",
        "injury_status": "None",
        "news": "None"
      },
      {
        "id": "00-0035632",
        "name": "Amani Hooker",
        "team": "TEN",
        "position": "DB",
        "status": "Active",
        "injury_status": "None",
        "news": "None"
      }
    ]
  }
}
```
**Description:** Returns a list of all currently unlocked players by position groups and sorted by first name. 'Unlocked' means a player's game for the week has not yet started (or they are on a bye) and they are able to be submitted in lineups. <br>
**Requirements:** None
<br><br>

**URI:** /api/player?id={player_id}<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "player": {
    "id": "00-0023459",
    "name": "Aaron Rodgers",
    "team": "GB",
    "pos": "QB",
    "status": "Active",
    "injury_status": "Questionable",
    "news": "Rodgers completed 31 of 39 passes for 326 yards with two touchdowns ..."
  }
}
```
**Description:** Returns data about the player corresponding to the player ID specified. <br>
**Requirements:** Player ID must be valid.
<br><br>

**URI:** /api/team?id={team_id}<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "team": {
    "id": "GB",
    "name": "Green Bay Packers"
  }
}
```
**Description:** Returns data about the team corresponding to the team ID specified. <br>
**Requirements:** Team ID must be valid. 
<br><br>

**URI:** /api/teams<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "teams": [
    {
      "id": "ARI",
      "name": "Arizona Cardinals"
    },
    {
      "id": "ATL",
      "name": "Atlanta Falcons"
    },
    {
      "id": "BAL",
      "name": "Baltimore Ravens"
    }
  ]
}
```
**Description:** Returns a list of all current active NFL teams.<br>
**Requirements:** None
<br><br>

**URI:** /api/week<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "current_week": {
    "season_type": "Regular",
    "season_year": 2019,
    "week": 17
  }
}
```
**Description:** Returns the season type, season year, and week corresponding to the current week of the season.<br> 
**Requirements:** None
<br><br>

**URI:** /api/games?seasonType=Regular&seasonYear=2019&week=17<br>
**Method:** GET<br>
**Sample response:**
```
{
  "success": true,
  "games": [
    {
      "id": "2019122900",
      "start_time": "2019-12-29 21:25",
      "season_type": "Regular",
      "season_year": 2019,
      "week": 17,
      "home_team": "BAL",
      "away_team": "PIT",
      "home_score": 28,
      "away_score": 10
    },
    {
      "id": "2019122901",
      "start_time": "2019-12-29 18:00",
      "season_type": "Regular",
      "season_year": 2019,
      "week": 17,
      "home_team": "BUF",
      "away_team": "NYJ",
      "home_score": 6,
      "away_score": 13
    },
    {
      "id": "2019122902",
      "start_time": "2019-12-29 18:00",
      "season_type": "Regular",
      "season_year": 2019,
      "week": 17,
      "home_team": "CAR",
      "away_team": "NO",
      "home_score": 10,
      "away_score": 42
    }
  ]
}
```
**Description:** Returns data about all the games scheduled for a given week.<br>
'seasonType', 'seasonYear', and 'week' are optional URI parameters that retrieve data for a specific week. If not provided, the current week is used.<br>
**Requirements:** Season type, season year, and week must refer to a valid season week.
<br><br>