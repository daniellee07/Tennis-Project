-- Change these names to compare players; each match is counted once from A's side.
SELECT a.player_name, b.player_name AS opponent, COUNT(*) AS matches,
       SUM(a.won) AS wins, 1.0*SUM(a.won)/COUNT(*) AS win_rate
FROM player_matches a JOIN player_matches b
  ON a.match_id=b.match_id AND a.player_id<>b.player_id
WHERE a.player_name='Novak Djokovic' AND b.player_name='Rafael Nadal'
GROUP BY a.player_id, b.player_id;
