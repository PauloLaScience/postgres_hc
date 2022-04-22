SELECT schemaname, relname, n_dead_tup as "Dead tuples",n_live_tup as "Live tuples", ROUND(CAST(n_dead_tup as numeric)/COALESCE(NULLIF(n_live_tup, 0),1), 2)  AS "Dead/Live Ratio",
 to_char(last_autovacuum,'dd/mm/yyyy') as "last autovacuum",
 to_char(last_autoanalyze,'dd/mm/yyyy') as "last autoanalyze"
FROM pg_stat_all_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
