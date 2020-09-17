# -*- coding: utf-8 -*-
'''Transform the yard line representations in the NFL stats data to remove the 
team identifier and make it instead a single integer from -50 (own goal line) to 
+50 (opponent's goal line)'''

def convert_yard_line(yard_line, team_id):
  # extract team ID and yardline ex. "GB 25" -> ['GB', 25]
  try:
    yard_line = yard_line.split(' ')
    team = yard_line[0]
    yard_value = int(yard_line[1])
  except:
    return None 
  # team's own yard line is negative, opponent's is positive
  # ex. GB on the GB 25 = -25, GB on the CHI 25 = 25
  if team == possession_team:
    return -1 * yard_value
  else:
    return yard_value