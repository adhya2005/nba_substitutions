import pandas as pd
pd.set_option("display.max_columns",None)
pd.set_option("display.max_rows",None)
pd.options.display.width = 0
pd.set_option('display.float_format', '{:.2f}'.format)
pd.options.display.max_colwidth = 200

df = pd.read_csv("2024_PBP.csv",index_col = 0)

# creates the string of the five players on the court for every row
def create_home_lineup_col(s):
    h1,h2,h3,h4,h5 = s['HOME_PLAYER1'],s['HOME_PLAYER2'],s['HOME_PLAYER3'],s['HOME_PLAYER4'],s['HOME_PLAYER5']
    return '-'.join(sorted([str(h) for h in [h1,h2,h3,h4,h5]]))
df['HOMELINEUP'] = df.apply(create_home_lineup_col,axis = 1)

def create_away_lineup_col(s):
    a1,a2,a3,a4,a5 = s['AWAY_PLAYER1'],s['AWAY_PLAYER2'],s['AWAY_PLAYER3'],s['AWAY_PLAYER4'],s['AWAY_PLAYER5']
    return '-'.join(sorted([str(a) for a in [a1,a2,a3,a4,a5]]))
df['AWAYLINEUP'] = df.apply(create_away_lineup_col,axis = 1)


# shifts the lineups by 1 row to see the previous lineup (to see which lineup we transition from)
df['HOMELINEUP_prev'] = df.groupby('GAME_ID')['HOMELINEUP'].shift()
df['AWAYLINEUP_prev'] = df.groupby('GAME_ID')['AWAYLINEUP'].shift()

# converts seconds elapsed (in game time) into minutes
df['game_time_elapsed'] = df['PCTIMESTRING'].astype(float)

# fixes the SCOREMARGIN column to make it of integer type
df['SCOREMARGIN'] = df['SCOREMARGIN'].replace('TIE',0)
df['SCOREMARGIN'] = df.groupby("GAME_ID")['SCOREMARGIN'].ffill()
df['SCOREMARGIN'] = df['SCOREMARGIN'].fillna(0).astype(int)




# SUBS only contains rows with  substitutions
df = df.reset_index(drop=True)
GAME_START = (df['EVENTMSGTYPE']==12)&(df['PERIOD'] ==1)
game_ending_indices = df.groupby("GAME_ID").tail(1).index.values.tolist()
GAME_END = df.index.isin( game_ending_indices )
ROW_SUBS = df['EVENTMSGTYPE'] == 8
SUBS = df[GAME_START|ROW_SUBS|GAME_END]

#SUBS = df[ROW_SUBS]

# HOME_SUBS are the rows with home substitutions
HOME_SUBS = SUBS[SUBS['VISITORDESCRIPTION'].isna()].copy()
AWAY_SUBS = SUBS[SUBS['HOMEDESCRIPTION'].isna()].copy()


# this column stores how long this lineup was on the floor
HOME_SUBS['time_on_floor'] = HOME_SUBS.groupby('GAME_ID')['game_time_elapsed'].diff()
AWAY_SUBS['time_on_floor'] = AWAY_SUBS.groupby('GAME_ID')['game_time_elapsed'].diff()
# this column stores the score margin (the plus or minus) of the five-man lineup
HOME_SUBS['PLUSMINUS'] = HOME_SUBS.groupby('GAME_ID')['SCOREMARGIN'].diff().fillna(0)
AWAY_SUBS['PLUSMINUS'] = AWAY_SUBS.groupby('GAME_ID')['SCOREMARGIN'].diff().fillna(0)

#HOME_SUBS['pm_prev'] = HOME_SUBS.groupby('GAME_ID')['PLUSMINUS'].shift()
#AWAY_SUBS['pm_prev'] = AWAY_SUBS.groupby('GAME_ID')['PLUSMINUS'].shift()

# this fills the null values of 'time_on_floor' with values from the 'game_time_elapsed' column
HOME_SUBS['time_on_floor'] = HOME_SUBS['time_on_floor'].fillna(HOME_SUBS['game_time_elapsed'])
AWAY_SUBS['time_on_floor'] = AWAY_SUBS['time_on_floor'].fillna(AWAY_SUBS['game_time_elapsed'])







# Wrangle the Home Substitutions

H = HOME_SUBS.loc[:,['GAME_ID','HOMELINEUP_prev','HOMELINEUP','time_on_floor','game_time_elapsed','SCORE','SCOREMARGIN','PLUSMINUS']].copy()
H = H.rename(columns = {'HOMELINEUP_prev':'lineup_prev','HOMELINEUP':'lineup','time_on_floor':'tof'})
H['tof_next'] = H.groupby(['GAME_ID'])['tof'].shift(-1)
H = H[~((H['tof']==0)&(H['tof_next']==0))]
H['tof_prev'] = H.groupby(['GAME_ID'])['tof'].shift()
H['lineup_prev2'] = H.groupby('GAME_ID')['lineup_prev'].shift()
#H['pm_prev2'] = H.groupby('GAME_ID')['pm_prev'].shift()
HH = H.copy()
HH.loc[HH['tof']==0,'lineup_prev'] =  HH.loc[HH['tof']==0,'lineup_prev2']
HH.loc[HH['tof']==0,'tof'] =  HH.loc[HH['tof']==0,'tof_prev']
HH = HH[HH['tof_next']!=0]
HH = HH.loc[:,['GAME_ID','lineup_prev','lineup','tof','game_time_elapsed','SCORE','SCOREMARGIN','PLUSMINUS']]
HH['PLUSMINUS'] = HH.groupby("GAME_ID")['SCOREMARGIN'].diff()
HH = HH.dropna(subset=['lineup_prev'])
HH['is_home'] = True


# Wrangle the AWAY subs


A = AWAY_SUBS.loc[:,['GAME_ID','HOMELINEUP_prev','HOMELINEUP','time_on_floor','game_time_elapsed','SCORE','SCOREMARGIN','PLUSMINUS']].copy()
A = A.rename(columns = {'HOMELINEUP_prev':'lineup_prev','HOMELINEUP':'lineup','time_on_floor':'tof'})
A['tof_next'] = A.groupby(['GAME_ID'])['tof'].shift(-1)
A = A[~((A['tof']==0)&(A['tof_next']==0))]
A['tof_prev'] = A.groupby(['GAME_ID'])['tof'].shift()
A['lineup_prev2'] = A.groupby('GAME_ID')['lineup_prev'].shift()
AA = A.copy()
AA.loc[AA['tof']==0,'lineup_prev'] =  AA.loc[AA['tof']==0,'lineup_prev2']
AA.loc[AA['tof']==0,'tof'] =  AA.loc[AA['tof']==0,'tof_prev']
AA = AA[AA['tof_next']!=0]
AA = AA.loc[:,['GAME_ID','lineup_prev','lineup','tof','game_time_elapsed','SCORE','SCOREMARGIN','PLUSMINUS']]
AA['PLUSMINUS'] = AA.groupby("GAME_ID")['SCOREMARGIN'].diff()
AA = AA.dropna(subset=['lineup_prev'])
AA['is_home'] = False




SUBSTITUTIONS = pd.concat([HH,AA]).reset_index(drop=True).set_index("GAME_ID")

S = SUBSTITUTIONS
S.loc[~S['is_home'],'SCOREMARGIN'] = -S.loc[~S['is_home'],'SCOREMARGIN']
S.loc[~S['is_home'],'PLUSMINUS'] = -S.loc[~S['is_home'],'PLUSMINUS']

SUBSTITUTIONS = S





