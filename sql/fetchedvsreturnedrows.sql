--fetched vs returned
select datname ,  tup_fetched "returned rows" , tup_returned "rows scanned" ,round(CAST(tup_fetched as decimal) / CAST(tup_returned as decimal) *100,2) as "percent fetched" from pg_stat_database where tup_returned!=0 
