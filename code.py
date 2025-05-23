import nba_api.stats.endpoints as nba
gid = '0042400312'
pbp = nba.playbyplayv2.PlayByPlayV2(game_id=gid).play_by_play.get_data_frame()
pbp_with_players = players_on_court(pbp)
pbp_with_players.iloc[[38,39]].T
