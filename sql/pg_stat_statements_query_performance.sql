--https://www.citusdata.com/blog/2019/03/29/health-checks-for-your-postgres-database/
SELECT query,
       calls,
       total_time,
       total_time / calls as time_per,
       stddev_time,
       rows,
       rows / calls as rows_per,
       100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE query not similar to '%pg_%'
and calls > 500
--ORDER BY calls
--ORDER BY total_time
order by time_per
--ORDER BY rows_per
DESC LIMIT 20;
