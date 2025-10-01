import pandas as pd
pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.options.display.width = 0
pd.set_option('display.float_format', '{:.2f}'.format)
pd.options.display.max_colwidth = 200

df = pd.read_csv("2024_PBP.csv")

# creates the string of the five players on the court for every row
def create_home_lineup_col(s):
    h1,h2,h3,h4,h5 = s['HOME_PLAYER1'],s['HOME_PLAYER2'],s['HOME_PLAYER3'],s['HOME_PLAYER4'],s['HOME_PLAYER5']
    return '-'.join(sorted([str(h) for h in [h1,h2,h3,h4,h5]]))
df['HOMELINEUP'] = df.apply(create_home_lineup_col,axis = 1)

def create_away_lineup_col(s):
    a1,a2,a3,a4,a5 = s['AWAY_PLAYER1'],s['AWAY_PLAYER2'],s['AWAY_PLAYER3'],s['AWAY_PLAYER4'],s['AWAY_PLAYER5']
    return '-'.join(sorted([str(h) for h in [a1,a2,a3,a4,a5]]))
df['AWAYLINEUP'] = df.apply(create_away_lineup_col,axis = 1)


# shifts the lineups by 1 row to see the previous lineup (to see which lineup we transition from)
df['HOMELINEUP_prev'] = df.groupby('GAME_ID')['HOMELINEUP'].shift()
df['AWAYLINEUP_prev'] = df.groupby('GAME_ID')['AWAYLINEUP'].shift()

# converts seconds elapsed (in game time) into minutes
df['game_time_elapsed'] = df['PCTIMESTRING']/60.

# SUBS only contains rows with  substitutions
SUBS = df[df['EVENTMSGTYPE'] == 8]

# HOME_SUBS are the rows with home substitutions
HOME_SUBS = SUBS[SUBS['VISITORDESCRIPTION'].isna()].copy()
AWAY_SUBS = SUBS[SUBS['HOMEDESCRIPTION'].isna()].copy()


# this column stores how long this lineup was on the floor
HOME_SUBS['time_on_floor'] = HOME_SUBS.groupby('GAME_ID')['game_time_elapsed'].diff()
AWAY_SUBS['time_on_floor'] = AWAY_SUBS.groupby('GAME_ID')['game_time_elapsed'].diff()

print(HOME_SUBS.loc[:,['HOMELINEUP_prev','HOMELINEUP','time_on_floor']])

#SUBS = df[df['EVENTMSGTYPE'] == 8]
#print(SUBS.loc[:,['HOMELINEUP_prev','HOMELINEUP','AWAYLINEUP_prev','AWAYLINEUP']].head())

