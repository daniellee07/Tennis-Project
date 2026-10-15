SELECT year, surface, COUNT(*) AS player_rows, SUM(stats_available) AS covered_rows,
       1.0*SUM(stats_available)/COUNT(*) AS coverage,
       1.0*SUM("1stWon")/NULLIF(SUM("1stIn"),0) AS first_serve_won,
       1.0*SUM("2ndWon")/NULLIF(SUM(svpt)-SUM("1stIn"),0) AS second_serve_won
FROM player_matches GROUP BY year, surface;
