from nba_api.stats.endpoints import playbyplayv2
import nba_api.stats.endpoints as nba
import nba_on_court as noc
import time
import pandas as pd


season = input("Which season? \n")
season_type = "Playoffs"
#season_type = "Regular Season"
df = nba.TeamGameLogs(season_nullable=season,season_type_nullable=season_type).get_data_frames()[0]



GAME_IDS = sorted(df['GAME_ID'].unique().tolist())[:3]
gid  = GAME_IDS[0]
pbp = playbyplayv2.PlayByPlayV2(game_id=gid).play_by_play.get_data_frame()
PLAYBYPLAY = noc.players_on_court(pbp)
PLAYBYPLAY['GAME_ID'] = gid 
for gid in GAME_IDS[1:]:
    pbp = playbyplayv2.PlayByPlayV2(game_id=gid).play_by_play.get_data_frame()
    PBP = noc.players_on_court(pbp)
    PBP['GAME_ID'] = gid
    PLAYBYPLAY = pd.concat([PLAYBYPLAY,PBP])
    print(gid)
    time.sleep(0.5)

PLAYBYPLAY.to_csv(season+"_PBP.csv")
