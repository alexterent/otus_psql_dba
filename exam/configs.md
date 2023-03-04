# Конфигуарции БД

Раздличные конфигуарции PostgreSQL для сравнения производительности. 

____

### Конфигуарция для эксперимента №2

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: hdd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
```

### Конфигуарция для эксперимента №6

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: hdd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

huge_pages = off

random_page_cost = 1.0
```

postgresql.conf:
```
# - Background Writer -

bgwriter_delay = 1000ms                 # 10-10000ms between rounds
bgwriter_lru_maxpages = 10              # max buffers written/round, 0 disables
bgwriter_lru_multiplier = 1.0           # 0-10.0 multiplier on buffers scanned/round
bgwriter_flush_after = 1024kB           # measured in pages, 0 disables
```


### Конфигуарция для эксперимента №7

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: hdd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

vacuum_cost_delay = 2   
vacuum_cost_page_hit = 0  
vacuum_cost_page_miss = 10   
vacuum_cost_page_dirty = 20  
vacuum_cost_limit = 200

autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 5s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_insert_threshold = 1000
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_insert_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.05 
autovacuum_freeze_max_age = 200000000
autovacuum_multixact_freeze_max_age = 400000000
autovacuum_vacuum_cost_delay = 5ms
autovacuum_vacuum_cost_limit = -1 
```



### Конфигуарция для эксперимента №8

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: hdd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

vacuum_cost_delay = 2   
vacuum_cost_page_hit = 0  
vacuum_cost_page_miss = 10   
vacuum_cost_page_dirty = 20  
vacuum_cost_limit = 200

autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 5s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_insert_threshold = 1000
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_insert_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.05 
autovacuum_freeze_max_age = 200000000
autovacuum_multixact_freeze_max_age = 400000000
autovacuum_vacuum_cost_delay = 5ms
autovacuum_vacuum_cost_limit = -1 

synchronous_commit = off
```


postgresql.conf:
```
fsync = off
full_page_writes = off
```


### Конфигуарция для эксперимента №10

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: ssd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
```


### Конфигуарция для эксперимента №11

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: ssd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

vacuum_cost_delay = 2   
vacuum_cost_page_hit = 0  
vacuum_cost_page_miss = 10   
vacuum_cost_page_dirty = 20  
vacuum_cost_limit = 200

autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 5s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_insert_threshold = 1000
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_insert_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.05 
autovacuum_freeze_max_age = 200000000
autovacuum_multixact_freeze_max_age = 400000000
autovacuum_vacuum_cost_delay = 5ms
autovacuum_vacuum_cost_limit = -1 
```




### Конфигуарция для эксперимента №12

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: ssd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

vacuum_cost_delay = 0
vacuum_cost_page_hit = 0
vacuum_cost_page_miss = 5  
vacuum_cost_page_dirty = 5 
vacuum_cost_limit = 200

autovacuum = on
autovacuum_max_workers = 10
autovacuum_naptime = 1s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_insert_threshold = 1000
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_insert_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.05
autovacuum_freeze_max_age = 200000000
autovacuum_multixact_freeze_max_age = 400000000
autovacuum_vacuum_cost_delay = 5ms
autovacuum_vacuum_cost_limit = -1

```




### Конфигуарция для эксперимента №13

pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: ssd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

vacuum_cost_delay = 2   
vacuum_cost_page_hit = 0  
vacuum_cost_page_miss = 10   
vacuum_cost_page_dirty = 20  
vacuum_cost_limit = 200

autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = 5s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_insert_threshold = 1000
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_insert_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.05 
autovacuum_freeze_max_age = 200000000
autovacuum_multixact_freeze_max_age = 400000000
autovacuum_vacuum_cost_delay = 5ms
autovacuum_vacuum_cost_limit = -1 
 
synchronous_commit = off
```


postgresql.conf:
```
fsync = off
full_page_writes = off
```


### Конфигуарция для эксперимента №14
pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: hdd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

enable_sort = off    
enable_seqscan = off
enable_partition_pruning = off
enable_parallel_append = off
enable_parallel_hash = off
enable_nestloop = off
enable_bitmapscan = off
```



### Конфигуарция для эксперимента №15
pgtune.conf:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 16 GB
# CPUs num: 8
# Connections num: 200
# Data Storage: ssd

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

enable_sort = off    
enable_seqscan = off
enable_partition_pruning = off
enable_parallel_append = off
enable_parallel_hash = off
enable_nestloop = off
enable_bitmapscan = off
```