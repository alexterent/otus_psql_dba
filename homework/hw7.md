# Домашняя работа 7

Механизм блокировок

____

### Подготовка окружения

Создадим машину (4cpu/8ram/10gb) в Яндекс Облаке, установим PostgreSQL 14 и добавим настройки для подключения. 
Шаги установки описаны в [домашней работе 1](/homework/hw1.md).


Настроим журнал сообщени так, чтобы туда попадала информация о блокировках, удерживаемых более 200 миллисекунд.
Для этого в файле `postgresql.conf` изменим значения:
```
log_lock_waits = on
log_min_duration_statement = 200
```

Сделаем рестарт БД:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

Убедимся, что логирование длительных блокировок включено:
```postgresql
postgres=# show log_lock_waits;
 log_lock_waits 
----------------
 on
(1 row)
```

Создадим тестовую БД `testdb`, в ней создадим таблицу и вставим несколько значений:
```postgresql
create table persons(id serial, first_name text, second_name text); 
insert into persons(first_name, second_name) values('ivan', 'ivanov'); 
insert into persons(first_name, second_name) values('petr', 'petrov');
```

В **первой сессии** откроем транзакцию и сделаем update:
```postgresql
\set AUTOCOMMIT off
begin;
update persons set second_name = 'noname';
```

Во **второй сессии** попытаемся сразу сделать update:
```postgresql
testdb=# update persons set second_name = 'noname';
^CCancel request sent
ERROR:  canceling statement due to user request
CONTEXT:  while updating tuple (0,1) in relation "persons"
```
_*После некоторого ожидания делаем ctrl+c._


Далее посмотрим что находится в логах.
Для этого откроем файл логов:
```shell
$ sudo cat /var/lib/pgsql/14/data/log/postgresql-Sat.log
```

Результаты из лога:
```
2023-03-11 07:24:16.765 UTC [1885] LOG:  process 1885 still waiting for ShareLock on transaction 957 after 1000.172 ms
2023-03-11 07:24:16.765 UTC [1885] DETAIL:  Process holding the lock: 1826. Wait queue: 1885.
2023-03-11 07:24:16.765 UTC [1885] CONTEXT:  while updating tuple (0,1) in relation "persons"
2023-03-11 07:24:16.765 UTC [1885] STATEMENT:  update persons set second_name = 'noname';
2023-03-11 07:24:56.927 UTC [1885] ERROR:  canceling statement due to user request
2023-03-11 07:24:56.927 UTC [1885] CONTEXT:  while updating tuple (0,1) in relation "persons"
2023-03-11 07:24:56.927 UTC [1885] STATEMENT:  update persons set second_name = 'noname';
```

Первая запись уведомляет о том, что процесс открыл блокировку на выполнение операций к таблице 
и остановил другой процесс.

Попробуем воспроизвести ситуацию в трёх сессия и прочитать результаты из `pg_locks`.

Завершим транзакцию в **первой сессии** и повторим её снова:
```postgresql
end;
\set AUTOCOMMIT off
begin;
update persons set second_name = 'noname1';
```

Во **второй сессии** сделаем другой update:
```postgresql
end;
\set AUTOCOMMIT off
begin;
update persons set second_name = 'noname2';
```

В **третьей сессии** сделаем другой update:
```postgresql
end;
\set AUTOCOMMIT off
begin;
update persons set second_name = 'noname3';
```

В **четвёртой сессии** сделаем select запрос и посмотрим результаты в таблице `pg_locks`:
```postgresql
testdb=# select * from pg_locks \gx
-[ RECORD 1 ]------+------------------------------
locktype           | relation
database           | 16600
relation           | 12290
page               | 
tuple              | 
virtualxid         | 
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 6/7
pid                | 2085
mode               | AccessShareLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 2 ]------+------------------------------
locktype           | virtualxid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 6/7
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 6/7
pid                | 2085
mode               | ExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 3 ]------+------------------------------
locktype           | relation
database           | 16600
relation           | 16609
page               | 
tuple              | 
virtualxid         | 
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 5/12
pid                | 2030
mode               | RowExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 4 ]------+------------------------------
locktype           | virtualxid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 5/12
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 5/12
pid                | 2030
mode               | ExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 5 ]------+------------------------------
locktype           | relation
database           | 16600
relation           | 16609
page               | 
tuple              | 
virtualxid         | 
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 4/106
pid                | 1974
mode               | RowExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 6 ]------+------------------------------
locktype           | virtualxid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 4/106
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 4/106
pid                | 1974
mode               | ExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 7 ]------+------------------------------
locktype           | relation
database           | 16600
relation           | 16609
page               | 
tuple              | 
virtualxid         | 
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 3/22
pid                | 1826
mode               | RowExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 8 ]------+------------------------------
locktype           | virtualxid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 3/22
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 3/22
pid                | 1826
mode               | ExclusiveLock
granted            | t
fastpath           | t
waitstart          | 
-[ RECORD 9 ]------+------------------------------
locktype           | transactionid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 
transactionid      | 959
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 3/22
pid                | 1826
mode               | ExclusiveLock
granted            | t
fastpath           | f
waitstart          | 
-[ RECORD 10 ]-----+------------------------------
locktype           | transactionid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 
transactionid      | 961
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 5/12
pid                | 2030
mode               | ExclusiveLock
granted            | t
fastpath           | f
waitstart          | 
-[ RECORD 11 ]-----+------------------------------
locktype           | tuple
database           | 16600
relation           | 16609
page               | 0
tuple              | 3
virtualxid         | 
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 4/106
pid                | 1974
mode               | ExclusiveLock
granted            | t
fastpath           | f
waitstart          | 
-[ RECORD 12 ]-----+------------------------------
locktype           | transactionid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 
transactionid      | 959
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 4/106
pid                | 1974
mode               | ShareLock
granted            | f
fastpath           | f
waitstart          | 2023-03-11 07:41:20.432492+00
-[ RECORD 13 ]-----+------------------------------
locktype           | tuple
database           | 16600
relation           | 16609
page               | 0
tuple              | 3
virtualxid         | 
transactionid      | 
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 5/12
pid                | 2030
mode               | ExclusiveLock
granted            | f
fastpath           | f
waitstart          | 2023-03-11 07:42:15.249423+00
-[ RECORD 14 ]-----+------------------------------
locktype           | transactionid
database           | 
relation           | 
page               | 
tuple              | 
virtualxid         | 
transactionid      | 960
classid            | 
objid              | 
objsubid           | 
virtualtransaction | 4/106
pid                | 1974
mode               | ExclusiveLock
granted            | t
fastpath           | f
waitstart          |
```

Узнаем что означают значения:
```
relation           | 12290
relation           | 16609
```

Для этого сделаем select запросы к таблице `pg_class`:
```postgresql
testdb=# select * from pg_class where oid = 12290 \gx
-[ RECORD 1 ]-------+----------------------------------------
oid                 | 12290
relname             | pg_locks
...

testdb=# select * from pg_class where oid = 16609 \gx
-[ RECORD 1 ]-------+--------
oid                 | 16609
relname             | persons
...
```

Далее обработаем вывод из таблицы `pg_locks`:

Процесс pid=2085 вызвал блокировку pg_locks в режиме AccessShareLock.
Процесс pid=2030 заблокировал таблицу persons в режиме RowExclusiveLock.
Процесс pid=1974 заблокировал таблицу persons в режиме RowExclusiveLock.
Процесс pid=1826 заблокировал таблицу persons в режиме RowExclusiveLock.
У каждой незавершённой транзакции есть запись с transactionid.



Добавим ещё одну строчку для update: 
```postgresql
testdb=# insert into persons(first_name, second_name) values('maria', 'noname100');
INSERT 0 1
```

В **первой сессии** сделаем update:
```postgresql
testdb=# \set AUTOCOMMIT off
testdb=# update persons set second_name = 'ivanov' where id = 1;
UPDATE 1
```

Во **второй сессии** сделаем update:
```postgresql
testdb=# \set AUTOCOMMIT off
testdb=# update persons set second_name = 'petrov' where id = 2;
UPDATE 1
```

В **третьей сессии** сделаем update:
```postgresql
testdb=# \set AUTOCOMMIT off
testdb=# update persons set second_name = 'michailovna' where id = 3;
UPDATE 1
```

В **первой сессии** повторим update:
```postgresql
testdb=*# update persons set second_name = 'p_2' where id = 2;
```

Во **второй сессии** повторим update:
```postgresql
testdb=*# update persons set second_name = 'p_3' where id = 3;
UPDATE 1
```

В **третьей сессии** повторим update и получим ошибку `deadlock detected`:
```postgresql
testdb=*# update persons set second_name = 'p_1' where id = 1;
ERROR:  deadlock detected
DETAIL:  Process 2030 waits for ShareLock on transaction 968; blocked by process 1826.
Process 1826 waits for ShareLock on transaction 969; blocked by process 1974.
Process 1974 waits for ShareLock on transaction 970; blocked by process 2030.
HINT:  See server log for query details.
CONTEXT:  while updating tuple (0,11) in relation "persons"
```

Посмотрим, что в журнале:
```
2023-03-11 08:10:02.468 UTC [1826] LOG:  process 1826 still waiting for ShareLock on transaction 969 after 1000.124 ms
2023-03-11 08:10:02.468 UTC [1826] DETAIL:  Process holding the lock: 1974. Wait queue: 1826.
2023-03-11 08:10:02.468 UTC [1826] CONTEXT:  while updating tuple (0,12) in relation "persons"
2023-03-11 08:10:02.468 UTC [1826] STATEMENT:  update persons set second_name = 'p_2' where id = 2;
2023-03-11 08:10:32.380 UTC [1974] LOG:  process 1974 still waiting for ShareLock on transaction 970 after 1000.111 ms
2023-03-11 08:10:32.380 UTC [1974] DETAIL:  Process holding the lock: 2030. Wait queue: 1974.
2023-03-11 08:10:32.380 UTC [1974] CONTEXT:  while updating tuple (0,13) in relation "persons"
2023-03-11 08:10:32.380 UTC [1974] STATEMENT:  update persons set second_name = 'p_3' where id = 3;
2023-03-11 08:10:43.548 UTC [2030] LOG:  process 2030 detected deadlock while waiting for ShareLock on transaction 968 after 1000.107 ms
2023-03-11 08:10:43.548 UTC [2030] DETAIL:  Process holding the lock: 1826. Wait queue: .
2023-03-11 08:10:43.548 UTC [2030] CONTEXT:  while updating tuple (0,11) in relation "persons"
2023-03-11 08:10:43.548 UTC [2030] STATEMENT:  update persons set second_name = 'p_1' where id = 1;
2023-03-11 08:10:43.548 UTC [2030] ERROR:  deadlock detected
2023-03-11 08:10:43.548 UTC [2030] DETAIL:  Process 2030 waits for ShareLock on transaction 968; blocked by process 1826.
	Process 1826 waits for ShareLock on transaction 969; blocked by process 1974.
	Process 1974 waits for ShareLock on transaction 970; blocked by process 2030.
	Process 2030: update persons set second_name = 'p_1' where id = 1;
	Process 1826: update persons set second_name = 'p_2' where id = 2;
	Process 1974: update persons set second_name = 'p_3' where id = 3;
2023-03-11 08:10:43.548 UTC [2030] HINT:  See server log for query details.
2023-03-11 08:10:43.548 UTC [2030] CONTEXT:  while updating tuple (0,11) in relation "persons"
2023-03-11 08:10:43.548 UTC [2030] STATEMENT:  update persons set second_name = 'p_1' where id = 1;
2023-03-11 08:10:43.548 UTC [1974] LOG:  process 1974 acquired ShareLock on transaction 970 after 12167.962 ms
2023-03-11 08:10:43.548 UTC [1974] CONTEXT:  while updating tuple (0,13) in relation "persons"
2023-03-11 08:10:43.548 UTC [1974] STATEMENT:  update persons set second_name = 'p_3' where id = 3;
2023-03-11 08:10:43.548 UTC [1974] LOG:  duration: 12168.234 ms  statement: update persons set second_name = 'p_3' where id = 3;
```

В журнале отображена ошибка `ERROR:  deadlock detected` и пояснение, почему она вышла, 
и какие процессы вызвали эту ошибку.


Две транзакции, выполняющие единственную команду UPDATE одной и той же таблицы (без where), 
НЕ МОГУТ заблокировать друг друга (вызвать deadlock detected). В примере выше был использован UPDATE без where 
и мы получили один update и второй зависший. В случае с update две транзакции не могут иметь блокировку с типом ROW EXCLUSIVE.
