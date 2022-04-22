--Total database size
SELECT pg_size_pretty( SUM(pg_database_size(datname))::bigint ) FROM pg_database
