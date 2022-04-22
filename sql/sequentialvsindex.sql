--Sequential vs index
select relname , seq_scan , idx_scan, 100 * idx_scan / (seq_scan + idx_scan)  Idx_usage_percent
from pg_stat_user_tables
WHERE seq_scan + idx_scan > 1
order by seq_scan  desc
