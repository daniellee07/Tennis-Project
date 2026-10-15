SELECT player_id, player_name, year, COUNT(*) AS matches, SUM(won) AS wins,
       1.0*SUM(won)/COUNT(*) AS win_rate
FROM player_matches GROUP BY player_id, player_name, year;
