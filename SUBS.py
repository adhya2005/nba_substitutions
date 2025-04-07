import nba_api.stats.endpoints as e
import re
import pandas as pd


"""
Example code for getting lineup information

"""


E = e.TeamGameLogs(season_nullable='2024-25').get_data_frames()[0]
HOME_LOGS = E[E['MATCHUP'].str.contains('vs.')]

# Let's look at the most recent game in the dataset
gid = HOME_LOGS['GAME_ID'].iloc[0]
team_id = HOME_LOGS['TEAM_ID'].iloc[0]

# Get box score to obtain home and away starters for the game
B = e.BoxScoreTraditionalV2(game_id=gid).get_data_frames()[0]
STARTERS = B[B['START_POSITION']!='']

home_starters = '-'.join(sorted([str(i) for i in STARTERS[STARTERS['TEAM_ID'] == team_id]['PLAYER_ID'].values.tolist()]))
away_starters = '-'.join(sorted([str(i) for i in STARTERS[STARTERS['TEAM_ID'] != team_id]['PLAYER_ID'].values.tolist()]))

print("Home starters concatenated player IDS:", home_starters)

# Get Play by Play data for this game
P2 = e.PlayByPlayV2(game_id=gid).get_data_frames()[0]




# create a minutes elapsed column using the game time column
def timestring_to_elapsed(series):
    p=series['PCTIMESTRING']
    q=series['PERIOD']
    t=p.split(":")
    min_remain,secs_remain=int(t[0]),float(t[1])
    time=11-min_remain+(60-secs_remain)/60.
    z=0
    if q<=4:
        z=12*(q-1)
    else:
        time=time-7
        z = 48+5*(q-5)
    return z+time

P2['minutes_elapsed'] = P2.apply(timestring_to_elapsed,axis=1)





# Substitutions are when the event message type is equal to 8
SUBS = P2[P2['EVENTMSGTYPE']==8].loc[:,['PERSON1TYPE','PLAYER1_ID','PERSON2TYPE','PLAYER2_ID','minutes_elapsed']]

# home sub events are when the person1type is 4, away is when it is 5
HOME_SUBS = SUBS[SUBS['PERSON1TYPE'] == 4].copy()
AWAY_SUBS = SUBS[SUBS['PERSON1TYPE'] == 5].copy()






































# Example Home sub data
HOME_SUBS = HOME_SUBS.loc[:,['PLAYER1_ID','PLAYER2_ID','minutes_elapsed']]



# Get first half substitutions
#
#
#
#
#
FIRST_HALF_HOME = HOME_SUBS[HOME_SUBS['minutes_elapsed'] <= 24].copy()

FIRST_HALF_HOME['time_on_court'] = FIRST_HALF_HOME['minutes_elapsed'].diff()
FIRST_HALF_HOME.loc[FIRST_HALF_HOME['time_on_court'].isna(),'time_on_court'] = FIRST_HALF_HOME.loc[FIRST_HALF_HOME['time_on_court'].isna(),'minutes_elapsed']
FIRST_HALF_HOME['time_on_court_next'] = FIRST_HALF_HOME['time_on_court'].shift(-1)
FIRST_HALF_HOME['PLAYER1_ID'] = FIRST_HALF_HOME['PLAYER1_ID'].astype(int).astype(str)
FIRST_HALF_HOME['PLAYER2_ID'] = FIRST_HALF_HOME['PLAYER2_ID'].astype(int).astype(str)
def fix_toc(s):
    if s == 0.0:
        return None
    else:
        return s
FIRST_HALF_HOME['time_on_court'] = FIRST_HALF_HOME['time_on_court'].apply(fix_toc)
FIRST_HALF_HOME['time_on_court'] = FIRST_HALF_HOME['time_on_court'].ffill()



starters = home_starters
data = []
old_lineup=starters
new_lineup = old_lineup
for row in FIRST_HALF_HOME.iterrows():
    toc = row[1]['time_on_court']
    toc_next = row[1]['time_on_court_next']
    min_elapsed = row[1]['minutes_elapsed']
    p_out = str(row[1]['PLAYER1_ID'])
    p_in = str(row[1]['PLAYER2_ID'])
    new_lineup = re.sub(p_out,p_in,new_lineup)
    new_lineup = '-'.join(sorted(new_lineup.split('-')))
    if toc_next == 0.:
        continue
    data.append([old_lineup,new_lineup,min_elapsed,toc])
    old_lineup=new_lineup

last_lineup_mins = 24.0 - FIRST_HALF_HOME['minutes_elapsed'].iloc[-1]
data.append([new_lineup,None,24.0,last_lineup_mins])


#
#
#
#
#
#












# Get second half substitutions
#
#
#
#
#
SECOND_HALF_HOME = HOME_SUBS[HOME_SUBS['minutes_elapsed'] > 24].copy()

SECOND_HALF_HOME['time_on_court'] = SECOND_HALF_HOME['minutes_elapsed'].diff()
SECOND_HALF_HOME.loc[SECOND_HALF_HOME['time_on_court'].isna(),'time_on_court'] = SECOND_HALF_HOME.loc[SECOND_HALF_HOME['time_on_court'].isna(),'minutes_elapsed'] - 24
SECOND_HALF_HOME['time_on_court_next'] = SECOND_HALF_HOME['time_on_court'].shift(-1)
SECOND_HALF_HOME['PLAYER1_ID'] = SECOND_HALF_HOME['PLAYER1_ID'].astype(int).astype(str)
SECOND_HALF_HOME['PLAYER2_ID'] = SECOND_HALF_HOME['PLAYER2_ID'].astype(int).astype(str)
def fix_toc(s):
    if s == 0.0:
        return None
    else:
        return s
SECOND_HALF_HOME['time_on_court'] = SECOND_HALF_HOME['time_on_court'].apply(fix_toc)
SECOND_HALF_HOME['time_on_court'] = SECOND_HALF_HOME['time_on_court'].ffill()


# BAD ASSUMPTION HERE
SECOND_HALF_HOME_starters = home_starters
old_lineup=SECOND_HALF_HOME_starters
new_lineup = old_lineup
for row in SECOND_HALF_HOME.iterrows():
    toc = row[1]['time_on_court']
    toc_next = row[1]['time_on_court_next']
    min_elapsed = row[1]['minutes_elapsed']
    p_out = str(row[1]['PLAYER1_ID'])
    p_in = str(row[1]['PLAYER2_ID'])
    new_lineup = re.sub(p_out,p_in,new_lineup)
    new_lineup = '-'.join(sorted(new_lineup.split('-')))
    if toc_next == 0.:
        continue
    data.append([old_lineup,new_lineup,min_elapsed,toc])
    old_lineup=new_lineup

total_minutes = P2['minutes_elapsed'].iloc[-1]
last_lineup_mins = total_minutes - HOME_SUBS['minutes_elapsed'].iloc[-1]
data.append([new_lineup,None,total_minutes,last_lineup_mins])
#
#
#
#
#
#





df_home = pd.DataFrame(data,columns = ['old_lineup','new_lineup','minutes_elapsed','time_on_floor'])






































































# Example Home sub data
AWAY_SUBS = AWAY_SUBS.loc[:,['PLAYER1_ID','PLAYER2_ID','minutes_elapsed']]



# Get first half substitutions
#
#
#
#
#
FIRST_HALF_AWAY = AWAY_SUBS[AWAY_SUBS['minutes_elapsed'] <= 24].copy()

FIRST_HALF_AWAY['time_on_court'] = FIRST_HALF_AWAY['minutes_elapsed'].diff()
FIRST_HALF_AWAY.loc[FIRST_HALF_AWAY['time_on_court'].isna(),'time_on_court'] = FIRST_HALF_AWAY.loc[FIRST_HALF_AWAY['time_on_court'].isna(),'minutes_elapsed']
FIRST_HALF_AWAY['time_on_court_next'] = FIRST_HALF_AWAY['time_on_court'].shift(-1)
FIRST_HALF_AWAY['PLAYER1_ID'] = FIRST_HALF_AWAY['PLAYER1_ID'].astype(int).astype(str)
FIRST_HALF_AWAY['PLAYER2_ID'] = FIRST_HALF_AWAY['PLAYER2_ID'].astype(int).astype(str)
def fix_toc(s):
    if s == 0.0:
        return None
    else:
        return s
FIRST_HALF_AWAY['time_on_court'] = FIRST_HALF_AWAY['time_on_court'].apply(fix_toc)
FIRST_HALF_AWAY['time_on_court'] = FIRST_HALF_AWAY['time_on_court'].ffill()



starters = away_starters
data = []
old_lineup=starters
new_lineup = old_lineup
for row in FIRST_HALF_AWAY.iterrows():
    toc = row[1]['time_on_court']
    toc_next = row[1]['time_on_court_next']
    min_elapsed = row[1]['minutes_elapsed']
    p_out = str(row[1]['PLAYER1_ID'])
    p_in = str(row[1]['PLAYER2_ID'])
    new_lineup = re.sub(p_out,p_in,new_lineup)
    new_lineup = '-'.join(sorted(new_lineup.split('-')))
    if toc_next == 0.:
        continue
    data.append([old_lineup,new_lineup,min_elapsed,toc])
    old_lineup=new_lineup

last_lineup_mins = 24.0 - FIRST_HALF_AWAY['minutes_elapsed'].iloc[-1]
data.append([new_lineup,None,24.0,last_lineup_mins])


#
#
#
#
#
#












# Get second half substitutions
#
#
#
#
#
SECOND_HALF_AWAY = AWAY_SUBS[AWAY_SUBS['minutes_elapsed'] > 24].copy()

SECOND_HALF_AWAY['time_on_court'] = SECOND_HALF_AWAY['minutes_elapsed'].diff()
SECOND_HALF_AWAY.loc[SECOND_HALF_AWAY['time_on_court'].isna(),'time_on_court'] = SECOND_HALF_AWAY.loc[SECOND_HALF_AWAY['time_on_court'].isna(),'minutes_elapsed'] - 24
SECOND_HALF_AWAY['time_on_court_next'] = SECOND_HALF_AWAY['time_on_court'].shift(-1)
SECOND_HALF_AWAY['PLAYER1_ID'] = SECOND_HALF_AWAY['PLAYER1_ID'].astype(int).astype(str)
SECOND_HALF_AWAY['PLAYER2_ID'] = SECOND_HALF_AWAY['PLAYER2_ID'].astype(int).astype(str)
def fix_toc(s):
    if s == 0.0:
        return None
    else:
        return s
SECOND_HALF_AWAY['time_on_court'] = SECOND_HALF_AWAY['time_on_court'].apply(fix_toc)
SECOND_HALF_AWAY['time_on_court'] = SECOND_HALF_AWAY['time_on_court'].ffill()


#BAD ASSUMPTION HERE. 
SECOND_HALF_AWAY_starters = away_starters
old_lineup=SECOND_HALF_AWAY_starters
new_lineup = old_lineup
for row in SECOND_HALF_AWAY.iterrows():
    toc = row[1]['time_on_court']
    toc_next = row[1]['time_on_court_next']
    min_elapsed = row[1]['minutes_elapsed']
    p_out = str(row[1]['PLAYER1_ID'])
    p_in = str(row[1]['PLAYER2_ID'])
    new_lineup = re.sub(p_out,p_in,new_lineup)
    new_lineup = '-'.join(sorted(new_lineup.split('-')))
    if toc_next == 0.:
        continue
    data.append([old_lineup,new_lineup,min_elapsed,toc])
    old_lineup=new_lineup

total_minutes = P2['minutes_elapsed'].iloc[-1]
last_lineup_mins = total_minutes - AWAY_SUBS['minutes_elapsed'].iloc[-1]
data.append([new_lineup,None,total_minutes,last_lineup_mins])
#
#
#
#
#
#





df_away = pd.DataFrame(data,columns = ['old_lineup','new_lineup','minutes_elapsed','time_on_floor'])








