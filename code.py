import nba_api.stats.endpoints as nba
import nba_on_court as noc
from nba_api.stats.endpoints import playbyplayv2

gid = '0042400312'
pbp = playbyplayv2.PlayByPlayV2(game_id=gid).play_by_play.get_data_frame()

pbp_with_players = noc.players_on_court(pbp)

players_id = list(pbp_with_players.iloc[0, 34:].reset_index(drop=True))
print(players_id)
[201142, 1629651, 201933, 201935, 203925, 201572, 201950, 1628960, 203114, 203507]

players_name = noc.players_name(players_id)
print(players_name)

pbp = nba.playbyplayv2.PlayByPlayV2(game_id=gid).play_by_play.get_data_frame()
pbp_with_players = players_on_court(pbp)
pbp_with_players.iloc[[38,39]].T
