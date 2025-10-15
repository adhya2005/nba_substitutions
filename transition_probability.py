import pandas as pd
import nba_api.stats.endpoints as e

S = pd.read_csv("substitutions.csv",index_col = 0)


GAMELOGS = e.TeamGameLogs(season_nullable="2024-25",season_type_nullable="Regular Season",league_id_nullable='00').get_data_frames()[0]
df = GAMELOGS.loc[:,['TEAM_ABBREVIATION','MATCHUP','GAME_ID']]

df = GAMELOGS.loc[:,['TEAM_ABBREVIATION','MATCHUP','GAME_ID']]
df = df.rename(columns = {"TEAM_ABBREVIATION":"team"})
df['is_home'] = df['MATCHUP'].str.contains("vs.")
df['GAME_ID']=df['GAME_ID'].astype(int)





#
# EXAMPLE Memphis Grizzlies trnasition probability calculation
#



### Get game ids and whetherh it is home or away for the memphis games
MEM = df[df['team'] == 'MEM']
MEM_home_game_ids = MEM.loc[MEM['is_home'],'GAME_ID'].values.tolist()
MEM_away_game_ids = MEM.loc[~MEM['is_home'],'GAME_ID'].values.tolist()
MEM_lineups = S[(S['GAME_ID'].isin(MEM_home_game_ids) & S['is_home']) | (S['GAME_ID'].isin(MEM_away_game_ids) & (~S['is_home']))]

# Number of states
Ni = MEM_lineups['lineup_prev'].unique().shape[0]

transition_probs = {}
for group,frame in MEM_lineups.groupby('lineup_prev'):
    k_vals = frame['lineup'].value_counts()
    k_vals = k_vals
    transition_probs[group] = k_vals

print(transition_probs)




#denominator = S[S['lineup_prev']=='-1627759-1628369-1628401-201143-201950-']['tof'].sum()
#denominator
#Lambda = numerator/denominator
#Lambda
#1/Lambda
#S[S['lineup_prev']=='-1627759-1628369-1628401-201143-201950-']['tof'].mean()
