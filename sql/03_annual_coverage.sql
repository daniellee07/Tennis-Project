SELECT year, COUNT(*) AS matches, MIN(date) AS first_tournament_date,
       MAX(date) AS last_tournament_date FROM matches GROUP BY year;
