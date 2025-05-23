import nba_api.stats.endpoints as nba
import time

seasons [str(year)+'-'str(year+1)[2:] for year in range(1996,2023)]
season = input("Which season? \n")
season_type = "Playoffs"
#season_type = "Regular Season"
df = nba.TeamGameLogs(season_nullable=season,season_type_nullable=season_type).get_data_frames()[0]

GAME_IDS = sorted(df['GAME_ID'].unique().tolist())
gid  = GAME_IDS[0]
PLAYBYPLAY = nba.PlayByPlayV3(game_id=gid).get_data_frames()[0]
PLAYBYPLAY['GAME_ID'] = gid
for gid in GAME_IDS[1:]:
    P = nba.PlayByPlayV2(game_id=gid).get_data_frames()[0]
    P['GAME_ID'] = gid
    PLAYBYPLAY = pd.concat([PLAYBYPLAY,P])
    print(gid)
    time.sleep(0.5)

PLAYBYPLAY.to_csv(season+"PBP.csv")
