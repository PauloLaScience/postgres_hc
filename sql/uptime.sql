select TO_CHAR((extract(epoch from now() - pg_postmaster_start_time()) || ' second')::interval, 'HH24:MI:SS')
