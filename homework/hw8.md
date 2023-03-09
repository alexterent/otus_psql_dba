# Домашняя работа 8

Нагрузочное тестирование и тюнинг PostgreSQL

____

### Подготовка окружения

Создадим машину (4cpu/8ram/10gb) в Яндекс Облаке, установим PostgreSQL 14 и добавим настройки для подключения. 
Шаги установки описаны в [домашней работе 1](/homework/hw1.md).

Далее установим необходимые библиотеки для pgbench как в [домашней работе 5](/homework/hw5.md).

### Стартовые показатели

Создадим таблицы для тестирования:
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
done in 0.48 s (drop tables 0.00 s, create tables 0.01 s, client-side generate 0.35 s, vacuum 0.05 s, primary keys 0.07 s).
```

Запустим простой `pgbench` на стандартной конфигурации PostgreSQL:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 538.0 tps, lat 91.782 ms stddev 95.524
progress: 20.0 s, 507.5 tps, lat 96.911 ms stddev 105.305
progress: 30.0 s, 505.6 tps, lat 100.216 ms stddev 115.830
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 15561
latency average = 96.391 ms
latency stddev = 105.781 ms
initial connection time = 55.356 ms
tps = 517.550744 (without initial connection time)
```

И запустим сложный тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -C -j 2 -P 10 -T 30 -M extended -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 265.9 tps, lat 179.661 ms stddev 193.748
progress: 20.0 s, 262.8 tps, lat 189.575 ms stddev 226.512
progress: 30.0 s, 279.6 tps, lat 175.635 ms stddev 222.513
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: extended
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 8132
latency average = 182.141 ms
latency stddev = 215.902 ms
average connection time = 2.439 ms
tps = 270.250726 (including reconnection times)
```

### Эксперимент 1

Введём все характеристики БД в pgtune и получим конфигурацию:
```
# DB Version: 14
# OS Type: linux
# DB Type: oltp
# Total Memory (RAM): 8 GB
# CPUs num: 4
# Data Storage: hdd

max_connections = 300
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 3495kB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
```

Далее создадим директорию `conf.d` в `/var/lib/pgsql/14/data` и сохраним в этой директории конфигурацию с pgtune:
```shell
$ sudo mkdir /var/lib/pgsql/14/data/conf.d/
$ sudo touch /var/lib/pgsql/14/data/conf.d/pgtune.conf
$ sudo vi /var/lib/pgsql/14/data/conf.d/pgtune.conf
```

В конце файла postgresql.conf добавим включение директории с дополнительными конфигами `include_dir = 'conf.d'`.

Сделаем рестарт БД:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

Запустим простой тест: 
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 623.6 tps, lat 78.718 ms stddev 82.527
progress: 20.0 s, 535.3 tps, lat 93.735 ms stddev 96.173
progress: 30.0 s, 544.8 tps, lat 91.827 ms stddev 111.971
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 17087
latency average = 87.831 ms
latency stddev = 97.343 ms
initial connection time = 57.441 ms
tps = 568.337807 (without initial connection time)
```

И запустим сложный тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -C -j 2 -P 10 -T 30 -M extended -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 258.7 tps, lat 187.378 ms stddev 209.546
progress: 20.0 s, 256.3 tps, lat 191.708 ms stddev 203.957
progress: 30.0 s, 279.3 tps, lat 177.568 ms stddev 208.613
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: extended
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 7993
latency average = 185.334 ms
latency stddev = 207.139 ms
average connection time = 2.468 ms
tps = 265.595442 (including reconnection times)
```

Показатели немного выросли в первом случае, и немного ниже во втором случае. 
Возможно, для сложного теста не хватило кол-ва итераций или времени, 
могло совпасть с какиси-нибудь процессами на самой ВМ, а также проблемами в Яндекс Облаке.
Можно предположить, что в целом не особо изменились показатели для второго случая.

### Эксперимент 2

Теперь отключим параметр `synchronous_commit`, чтобы сервер не сообщал об успешном выполнении операции. 
В файле `pgtune.conf` добавим строчку `synchronous_commit = off`.

Затем необходимо выполнить рестарт БД:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

Запустим простой тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 3327.9 tps, lat 14.913 ms stddev 14.462
progress: 20.0 s, 3373.1 tps, lat 14.813 ms stddev 14.111
progress: 30.0 s, 3363.4 tps, lat 14.865 ms stddev 14.715
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 100693
latency average = 14.873 ms
latency stddev = 14.443 ms
initial connection time = 52.861 ms
tps = 3357.585097 (without initial connection time)
```

И запустим сложный тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -C -j 2 -P 10 -T 30 -M extended -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 398.9 tps, lat 120.811 ms stddev 130.954
progress: 20.0 s, 406.5 tps, lat 118.770 ms stddev 147.482
progress: 30.0 s, 404.6 tps, lat 122.325 ms stddev 142.568
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: extended
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 12150
latency average = 120.537 ms
latency stddev = 140.352 ms
average connection time = 2.892 ms
tps = 404.460463 (including reconnection times)
```

Показатели выросли в несколько раз: в 6 раз в первом случае и в 2 раза во втором случае. 

### Эксперимент 3

Попробуем отключить ещё параметр `fsync` и `full_page_writes`. 
Первая настройка отключит прерывания на проверку записи данных на физический диск. 

В файл `postgres.conf` необходимо установить значения:
```
fsync = off
full_page_writes = off
```

Затем необходимо выполнить рестарт БД:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

Запустим простой тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 3368.8 tps, lat 14.739 ms stddev 14.009
progress: 20.0 s, 3414.6 tps, lat 14.624 ms stddev 14.261
progress: 30.0 s, 3397.3 tps, lat 14.724 ms stddev 14.716
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 101856
latency average = 14.705 ms
latency stddev = 14.343 ms
initial connection time = 52.586 ms
tps = 3396.416030 (without initial connection time)
```

И запустим сложный тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -c 50 -C -j 2 -P 10 -T 30 -M extended -U postgres postgres
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 402.8 tps, lat 119.383 ms stddev 110.871
progress: 20.0 s, 411.7 tps, lat 118.325 ms stddev 130.807
progress: 30.0 s, 406.6 tps, lat 120.176 ms stddev 134.852
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: extended
number of clients: 50
number of threads: 2
duration: 30 s
number of transactions actually processed: 12262
latency average = 119.404 ms
latency stddev = 126.252 ms
average connection time = 2.907 ms
tps = 408.144435 (including reconnection times)
```

Наблюдается небольшой прирост, но не такой, как между 1 и 2 экспериментом.

### Результаты

Используя pgtune для HDD, можно немного улучшить работу, но основной прирост к работе БД дало 
именно отключение параметров, отвечающих за целостность данных. Также работу pgtune, вероятно, 
будет лучше заметно на машинах, у которых большое кол-во CPU и RAM. 

В примере для домашней работы использовалась машина с 4 CPU и 8 RAM, поэтому большого прироста 
не было заметно после использования pgtune. Вероятно, используя pgtune на машине с 16 CPU и 32 RAM 
можно увидеть заметный прирост относительно дефолтных настроек PostgreSQL.
