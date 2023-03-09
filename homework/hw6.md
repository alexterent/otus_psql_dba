# Домашняя работа 6

Работа с журналами

____

### Подготовка окружения

Создадим машину (4cpu/8ram/10gb) в Яндекс Облаке, установим PostgreSQL 14 и добавим настройки для подключения. 
Шаги установки описаны в [домашней работе 1](/homework/hw1.md).

Далее установим необходимые библиотеки для pgbench как в [домашней работе 5](/homework/hw5.md).


### Настройка контрольной точки

В файле postgresql.conf установим минимальное значение для контрольных точек: `checkpoint_timeout = 30s`.

Сделаем рестарт БД:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

Далее создадим таблицы для теста pgbench:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -i -U postgres postgres
dropping old tables...
NOTICE:  table "pgbench_accounts" does not exist, skipping
NOTICE:  table "pgbench_branches" does not exist, skipping
NOTICE:  table "pgbench_history" does not exist, skipping
NOTICE:  table "pgbench_tellers" does not exist, skipping
creating tables...
generating data (client-side)...
100000 of 100000 tuples (100%) done (elapsed 0.01 s, remaining 0.00 s)
vacuuming...
creating primary keys...
done in 0.47 s (drop tables 0.00 s, create tables 0.01 s, client-side generate 0.33 s, vacuum 0.05 s, primary keys 0.08 s).
```

И запустим тест:
```shell
sudo /usr/pgsql-14/bin/pgbench -c8 -P 60 -T 600 -U postgres postgres 
pgbench (14.7)
starting vacuum...end.
progress: 60.0 s, 677.0 tps, lat 11.811 ms stddev 10.165
progress: 120.0 s, 667.2 tps, lat 11.990 ms stddev 8.886
progress: 180.0 s, 691.2 tps, lat 11.572 ms stddev 8.418
progress: 240.0 s, 702.5 tps, lat 11.386 ms stddev 8.555
progress: 300.0 s, 659.8 tps, lat 12.122 ms stddev 9.328
progress: 360.0 s, 670.1 tps, lat 11.937 ms stddev 8.774
progress: 420.0 s, 683.3 tps, lat 11.707 ms stddev 8.221
progress: 480.0 s, 615.5 tps, lat 12.998 ms stddev 9.734
progress: 540.0 s, 668.1 tps, lat 11.974 ms stddev 8.772
progress: 600.0 s, 687.8 tps, lat 11.629 ms stddev 8.086
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 8
number of threads: 1
duration: 600 s
number of transactions actually processed: 403352
latency average = 11.899 ms
latency stddev = 8.913 ms
initial connection time = 15.043 ms
tps = 672.247952 (without initial connection time)
```


После теста, проверим, появились ли контрольные точки:
```shell
$ sudo ls -hl /var/lib/pgsql/14/data/pg_wal/
итого 64M
-rw-------. 1 postgres postgres 16M фев 26 19:30 00000001000000000000001F
-rw-------. 1 postgres postgres 16M фев 26 19:28 000000010000000000000020
-rw-------. 1 postgres postgres 16M фев 26 19:29 000000010000000000000021
-rw-------. 1 postgres postgres 16M фев 26 19:29 000000010000000000000022
drwx------. 2 postgres postgres   6 фев 26 18:40 archive_status
```
На одну контрольную точку в среднем приходится 64 / 4 = 16 Mb


Далее проверим данные статистики:
```postgresql
postgres=# SELECT * FROM pg_stat_bgwriter \gx
-[ RECORD 1 ]---------+------------------------------
checkpoints_timed     | 44
checkpoints_req       | 1
checkpoint_write_time | 565201
checkpoint_sync_time  | 694
buffers_checkpoint    | 43328
buffers_clean         | 0
maxwritten_clean      | 0
buffers_backend       | 4416
buffers_backend_fsync | 0
buffers_alloc         | 4943
stats_reset           | 2023-02-26 18:44:30.397463+00
```

Одна из контрольных точек выполнилась по требованию, остальные по расписанию. 
Почти все точки выплонились по расписанию, т.к. задана высокая частота контрольных точек - один раз в 30 секунд.


### Сравнение tps в синхронном и асинхронном режимах 

По умолчанию в `postgresql.conf` установлено значение `synchronous_commit = on`. 
Запусти тест на 30 секунд с промежуточными результатами в 10 секунд:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -P 10 -T 30 -U postgres postgres 
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 418.9 tps, lat 2.385 ms stddev 3.497
progress: 20.0 s, 517.1 tps, lat 1.934 ms stddev 1.497
progress: 30.0 s, 590.4 tps, lat 1.694 ms stddev 1.268
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 1
number of threads: 1
duration: 30 s
number of transactions actually processed: 15265
latency average = 1.965 ms
latency stddev = 2.194 ms
initial connection time = 5.567 ms
tps = 508.909941 (without initial connection time)
```

Далее поменяем параметр на значение `synchronous_commit = off;` в файле `postgresql.conf`, 
а затем сделаем рестарт БД.
Запустим снова тест:
```shell
$ sudo /usr/pgsql-14/bin/pgbench -P 10 -T 30 -U postgres postgres 
pgbench (14.7)
starting vacuum...end.
progress: 10.0 s, 2479.9 tps, lat 0.403 ms stddev 0.071
progress: 20.0 s, 2102.3 tps, lat 0.475 ms stddev 0.031
progress: 30.0 s, 2141.8 tps, lat 0.467 ms stddev 0.278
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 1
query mode: simple
number of clients: 1
number of threads: 1
duration: 30 s
number of transactions actually processed: 67241
latency average = 0.446 ms
latency stddev = 0.167 ms
initial connection time = 2.548 ms
tps = 2241.547261 (without initial connection time)
```

В асинхронном режиме из-за отсутствия журналирования, значительно уменьшилось `latency` и увеличилось `tps`.


### Проверка кластера с включенной контрольной суммой страниц

Создадим новый кластер с включенной контрольной суммой страниц.
Для этого остановим текущий кластер, скопируем настройки для доступа, далее удалим всё содержимое 
папки `/var/lib/pgsql/`, добавим опцию котроля сумм в initdb, создадим новый кластер, 
вернём `pg_hba.conf` и сделаем рестарт БД:
```shell
sudo systemctl stop postgresql-14
sudo cp /var/lib/pgsql/14/data/pg_hba.conf /tmp/
sudo rm -rf /var/lib/pgsql/
export PGSETUP_INITDB_OPTIONS="--data-checksums"
sudo /usr/pgsql-14/bin/postgresql-14-setup initdb
sudo systemctl enable postgresql-14
sudo cp /tmp/pg_hba.conf /var/lib/pgsql/14/data/
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

Проверим, что контрольные суммы включены:
```postgresql

postgres=# show data_checksums ;
 data_checksums 
----------------
 on
(1 row)
```

**Примечание:** если export не установил переменную, то зайдите в скрипт `/usr/pgsql-14/bin/postgresql-14-setup` 
и добавьте опцию `--data-checksums` в initdb. 

Создадим таблицу и вставим несколько значений:
```postgresql
create table persons(id serial, first_name text, second_name text); 
insert into persons(first_name, second_name) values('ivan', 'ivanov'); 
insert into persons(first_name, second_name) values('petr', 'petrov');
```

Проверим, что таблица создалась:
```postgresql
postgres# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
(2 rows)
```

Узнаем, гре хранится эта таблица:
```postgresql
postgres=# SELECT pg_relation_filepath('persons');
 pg_relation_filepath 
----------------------
 base/14486/16385
(1 row)
```

Далее выключим кластер, найдём по указанному файлу, добавим в него цифру 1 и включим кластер:
```shell
$ sudo systemctl stop postgresql-14
$ sudo vi /var/lib/pgsql/14/data/base/14486/16385
$ sudo systemctl start postgresql-14
```

Сделаем выборку из таблицы:
```postgresql
postgres=# select * from persons;
WARNING:  page verification failed, calculated checksum 34697 but expected 30737
ERROR:  invalid page in block 0 of relation base/14486/16385
```

Т.к. теперь контрольные суммы отличаются, PostgreSQL вывел ошибку. 
Чтобы проигнорировать ошибку, нужно добавить `ignore_checksum_failure = on`.

```postgresql
postgres=# set ignore_checksum_failure = on;
SET
postgres=# select * from persons;
WARNING:  page verification failed, calculated checksum 34697 but expected 30737
 id | first_name | second_name 
----+------------+-------------
(0 rows)
```
