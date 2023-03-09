# Домашняя работа 5

Настройка autovacuum с учетом оптимальной производительности

____

### Подготовка для экспериментов с vacuum и autovacuum 

Создадим новую машину в Яндекс Облаке с параметрами: 

```
Total Memory (RAM): 4 GB
CPUs num: 2
Data Storage: hdd
Disk size: 10 Gb
OS: CentOS 7
```

и установим PostgreSQL 14. Шаги установки описаны в [домашней работе 1](/homework/hw1.md).

Для того, чтобы запустить `pgbench`, необходимо установить contrib:
```shell
sudo yum install postgresql-contrib
```

И подправить настройки для подключения postgres пользователя с local.
В файле pg_hba.conf заменить
```
local   all             postgres                                peer
```
на 
```
local   all             postgres                                trust
```

а в файле postgresql.conf расскомментировать строчку с настройкой: 
```
unix_socket_directories = '/var/run/postgresql/, /tmp'
```


Далее применим параметры настройки PostgreSQL. Для этого запустим редактор:
```shell
sudo vi /var/lib/pgsql/14/data/postgresql.conf
```

и подправим все значения из этого списка:
```
max_connections = 40
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 500
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 6553kB
min_wal_size = 4GB
max_wal_size = 16GB
```

Если кластер был запущен, то его нужно оставить и запустить. Если не был запущен, то только запустить:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```


Теперь можно запустить `pgbench`:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -i -U postgres postgres
dropping old tables...
NOTICE:  table "pgbench_accounts" does not exist, skipping
NOTICE:  table "pgbench_branches" does not exist, skipping
NOTICE:  table "pgbench_history" does not exist, skipping
NOTICE:  table "pgbench_tellers" does not exist, skipping
creating tables...
generating data (client-side)...
100000 of 100000 tuples (100%) done (elapsed 0.03 s, remaining 0.00 s)
vacuuming...
creating primary keys...
done in 0.51 s (drop tables 0.00 s, create tables 0.01 s, client-side generate 0.34 s, vacuum 0.06 s, primary keys 0.10 s).
```

Далее запустим с pgbench с настройками:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres 
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 593.1 tps, lat 13.477 ms stddev 9.022
progress: 120.0 s, 505.0 tps, lat 15.835 ms stddev 11.231
progress: 180.0 s, 481.9 tps, lat 16.596 ms stddev 11.179
progress: 240.0 s, 469.9 tps, lat 17.018 ms stddev 12.226
progress: 300.0 s, 482.5 tps, lat 16.578 ms stddev 10.389
progress: 360.0 s, 569.2 tps, lat 14.049 ms stddev 9.580
progress: 420.0 s, 559.6 tps, lat 14.289 ms stddev 8.935
progress: 480.0 s, 572.5 tps, lat 13.967 ms stddev 9.284
progress: 540.0 s, 567.8 tps, lat 14.084 ms stddev 8.752
progress: 600.0 s, 524.5 tps, lat 15.247 ms stddev 9.942
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 319574
latency average = 15.015 ms
latency stddev = 10.107 ms
initial connection time = 17.454 ms
tps = 532.620403 (without initial connection time)
```

### Эксперимент №1

Внесём изменения по `autovacuum` в `postgresql.conf`:
```
vacuum_cost_delay = 4   
vacuum_cost_page_hit = 1  
vacuum_cost_page_miss = 4   
vacuum_cost_page_dirty = 20  
vacuum_cost_limit = 500

autovacuum = on
autovacuum_max_workers = 2
autovacuum_naptime = 10s
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_insert_threshold = 1000
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.05
autovacuum_vacuum_insert_scale_factor = 0.05
autovacuum_analyze_scale_factor = 0.1 
autovacuum_freeze_max_age = 200000000
autovacuum_multixact_freeze_max_age = 400000000
autovacuum_vacuum_cost_delay = 5ms
autovacuum_vacuum_cost_limit = -1 
```

Перезапустим PostgreSQL при помощи `stop-start` и запустим `pgbench`:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres 
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 464.7 tps, lat 17.203 ms stddev 13.416
progress: 120.0 s, 493.1 tps, lat 16.218 ms stddev 10.688
progress: 180.0 s, 501.2 tps, lat 15.955 ms stddev 10.113
progress: 240.0 s, 545.9 tps, lat 14.653 ms stddev 9.298
progress: 300.0 s, 486.1 tps, lat 16.452 ms stddev 10.440
progress: 360.0 s, 536.3 tps, lat 14.911 ms stddev 9.782
progress: 420.0 s, 471.7 tps, lat 16.953 ms stddev 12.172
progress: 480.0 s, 507.2 tps, lat 15.766 ms stddev 9.777
progress: 540.0 s, 551.1 tps, lat 14.512 ms stddev 8.689
progress: 600.0 s, 529.0 tps, lat 15.119 ms stddev 9.558
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 305182
latency average = 15.723 ms
latency stddev = 10.447 ms
initial connection time = 18.867 ms
tps = 508.635560 (without initial connection time)
```

Результат по tps - ухудшился, но время выполнения на разных тестах скачет.

### Эксперимент №2

Попробуем изменить некоторые из параметров и запустить ещё раз. 
На этот раз изменим следующие параметры:
```
vacuum_cost_delay = 2                           # уменьшили
vacuum_cost_page_hit = 0                        # уменьшили
vacuum_cost_page_miss = 10                      # увеличили
vacuum_cost_limit = 200                         # уменьшили

autovacuum_max_workers = 4                      # увеличили
autovacuum_naptime = 5s                         # уменьшили
autovacuum_vacuum_insert_scale_factor = 0.2     # увеличили
autovacuum_analyze_scale_factor = 0.05          # уменьшили
```


Результаты запусков:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres 
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 448.3 tps, lat 17.827 ms stddev 12.895
progress: 120.0 s, 524.2 tps, lat 15.260 ms stddev 10.034
progress: 180.0 s, 463.4 tps, lat 17.252 ms stddev 12.565
progress: 240.0 s, 531.6 tps, lat 15.051 ms stddev 9.229
progress: 300.0 s, 504.5 tps, lat 15.852 ms stddev 10.941
progress: 360.0 s, 493.1 tps, lat 16.219 ms stddev 10.907
progress: 420.0 s, 607.3 tps, lat 13.167 ms stddev 7.530
progress: 480.0 s, 529.2 tps, lat 15.111 ms stddev 10.101
progress: 540.0 s, 550.4 tps, lat 14.531 ms stddev 9.487
progress: 600.0 s, 541.8 tps, lat 14.762 ms stddev 9.309
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 311633
latency average = 15.397 ms
latency stddev = 10.367 ms
initial connection time = 18.300 ms
tps = 519.385226 (without initial connection time)
```


```shell
sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 546.9 tps, lat 14.616 ms stddev 9.468
progress: 120.0 s, 537.8 tps, lat 14.872 ms stddev 9.859
progress: 180.0 s, 575.1 tps, lat 13.906 ms stddev 8.845
progress: 240.0 s, 528.3 tps, lat 15.139 ms stddev 9.727
progress: 300.0 s, 505.5 tps, lat 15.821 ms stddev 9.828
progress: 360.0 s, 548.6 tps, lat 14.577 ms stddev 9.214
progress: 420.0 s, 547.1 tps, lat 14.619 ms stddev 9.774
progress: 480.0 s, 524.0 tps, lat 15.263 ms stddev 9.798
progress: 540.0 s, 507.1 tps, lat 15.770 ms stddev 10.122
progress: 600.0 s, 555.6 tps, lat 14.395 ms stddev 8.720
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 322559
latency average = 14.876 ms
latency stddev = 9.549 ms
initial connection time = 17.699 ms
tps = 537.594677 (without initial connection time)
```

Как видно, даже разное время запуска в Яндекс Облаке, какие-то "вычислительные процессы на хосте"
влияют на время, т.е. два запуска на одной и той же конфигурации дали разное среднее tps, 
так и между разными сериями выполнений.

### Эксперимент №3

Попробуем изменить некоторые из параметров и запустить ещё раз. 
На этот раз изменим следующие параметры:

```
vacuum_cost_page_miss = 2               # уменьшили
vacuum_cost_page_dirty = 40             # увеличили
vacuum_cost_limit = 1000                # увеличили

autovacuum_naptime = 1s                 # уменьшили
autovacuum_vacuum_scale_factor = 0.02   # уменьшили
autovacuum_analyze_scale_factor = 0.02  # уменьшили
autovacuum_vacuum_cost_delay = 10ms     # увеличили
```



Результаты запусков:

```shell

$ sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 517.8 tps, lat 15.427 ms stddev 11.973
progress: 120.0 s, 434.0 tps, lat 18.440 ms stddev 14.188
progress: 180.0 s, 494.8 tps, lat 16.157 ms stddev 11.497
progress: 240.0 s, 483.8 tps, lat 16.536 ms stddev 12.027
progress: 300.0 s, 539.4 tps, lat 14.827 ms stddev 10.167
progress: 360.0 s, 506.6 tps, lat 15.785 ms stddev 11.534
progress: 420.0 s, 465.0 tps, lat 17.197 ms stddev 12.577
progress: 480.0 s, 527.9 tps, lat 15.152 ms stddev 10.345
progress: 540.0 s, 514.0 tps, lat 15.557 ms stddev 10.145
progress: 600.0 s, 400.2 tps, lat 19.988 ms stddev 16.411
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 293016
latency average = 16.376 ms
latency stddev = 12.153 ms
initial connection time = 17.598 ms
tps = 488.355010 (without initial connection time)

```


```shell
$ sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 523.7 tps, lat 15.263 ms stddev 10.390
progress: 120.0 s, 445.0 tps, lat 17.972 ms stddev 13.617
progress: 180.0 s, 519.6 tps, lat 15.391 ms stddev 10.590
progress: 240.0 s, 445.4 tps, lat 17.955 ms stddev 14.132
progress: 300.0 s, 493.0 tps, lat 16.219 ms stddev 10.997
progress: 360.0 s, 484.1 tps, lat 16.522 ms stddev 11.725
progress: 420.0 s, 447.7 tps, lat 17.863 ms stddev 13.369
progress: 480.0 s, 443.9 tps, lat 18.017 ms stddev 13.417
progress: 540.0 s, 476.7 tps, lat 16.779 ms stddev 11.855
progress: 600.0 s, 520.7 tps, lat 15.359 ms stddev 10.270
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 287998
latency average = 16.661 ms
latency stddev = 12.077 ms
initial connection time = 16.584 ms
tps = 479.992146 (without initial connection time)
```

При таких настройках смогли получить результат хуже; среднее tps гарантированно меньше, 
чем без настроек vacuum и autovacuum.


### Выводы 

Основной упор делался на подбор `vacuum_cost_*` значений и время вызова и работы `autovacuum_naptime`.
При условии, что используется HDD диск, следует делать больше времени между vacuum.
Большой `vacuum_cost_limit`, огромная разница между `vacuum_cost_page_miss` и `vacuum_cost_page_dirty`
и частое срабатывание autovacuum существенно занизили работу PostgreSQL в эксперименте №3.

Интересные результаты дал эксперимент №2, где `vacuum_cost_page_miss`=10, 
т.е. 1/2 от `vacuum_cost_page_dirty`, низким `vacuum_cost_limit` 
и с увеличенным `autovacuum_max_workers`. Работа такого кластера была практически такой же, 
как и без включения autovacuum.
