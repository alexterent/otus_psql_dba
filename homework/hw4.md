# Домашняя работа 4

Работа с базами данных, пользователями и правами

____

Запустим docker контейнер с Postgres из домашней работы №2.

Переключимся из-под пользователя homework1 на postgres:
```shell
psql -h localhost -U postgres -d postgres
```

Создадим новую базу данных `testdb`:
```postgresql
create database testdb;
```

Перезайдём в созданную БД `testdb` под пользователем `postgres`
```shell
exit;
psql -h localhost -U postgres -d testdb
```

Создадим новую схему `testnm`:
```postgresql
CREATE SCHEMA testnm;
```

И создадим в этой схеме таблицу `t1`:
```postgresql
create table testnm.t1(c1 integer); 
```

Далее сделаем вставку одной строки:
```postgresql
insert into testnm.t1(c1) values(1); 
```

И создадим новую роль readonly с правом на подключение к БД `testdb`, пользованием схемы `testnm`, 
и с правом на select для всех таблиц схемы `testnm`:
```postgresql
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE testdb TO readonly;
GRANT USAGE ON SCHEMA testnm TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA testnm TO readonly;
```

Создадим пользователя `testread` с паролем `test123`:
```postgresql
CREATE USER testread WITH PASSWORD 'test123';
```

И назначим для пользователя новую роль:
```postgresql
GRANT readonly TO testread;
```

Убедимся, что роль назначена: 
```postgresql
\du
                                    List of roles
 Role name |                         Attributes                         | Member
 of  
-----------+------------------------------------------------------------+-------
-----
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
 readonly  | Cannot login                                               | {}
 testread  |                                                            | {reado
nly}
```

Теперь зайдём под пользователем `testread` в БД `testdb`:
```postgresql
exit;
psql -h localhost -U testread -d testdb
```

И сделаем select запрос:
```postgresql
testdb=> select * from t1;
ERROR:  relation "t1" does not exist
СТРОКА 1: select * from t1;
                        ^

```

Перед именем таблицы укажем схему и повторим select запрос:
```postgresql
testdb=> select * from testnm.t1;
 c1 
----
  1
(1 строка)
```

В результате запросы без указания схемы приводили к ошибке.
Посмотрим, какие таблицы есть у этой схемы: 
```postgresql
testdb=> SELECT * FROM pg_catalog.pg_tables WHERE schemaname='testnm';
 schemaname | tablename | tableowner | tablespace | hasindexes | hasrules | hastriggers | rowsec
urity 
------------+-----------+------------+------------+------------+----------+-------------+-------
------
 testnm     | t1        | postgres   |            | f          | f        | f           | f
(1 строка)

```

Как видим, в схеме `testnm` есть таблица `t1`.
Если создать таблицу без указания схемы, то такая таблица попадёт в публичную схему `public`.
Если не указывать схему, то таблица ищется в схеме `public`.


Решить такую проблему ещё можно установкой путь поиска схем:

```postgresql
SET search_path TO my_schema, public;
```

или 
```postgresql
SET SCHEMA my_schema;
```


Переключимся на пользователя `postgres`:
```postgresql
testdb=> \c - postgres

Вы подключены к базе данных "testdb" как пользователь "postgres".
```

и удалим таблицу `t1`:
```postgresql
drop table testnm.t1;
```

Снова создадим таблицу `t1` со значением c1=1:
```postgresql
create table testnm.t1(c1 integer); 
insert into testnm.t1(c1) values(1); 
```

Зайдём под пользователем `testread` в базу данных `testdb`:
```postgresql
testdb=# \c - testread

Вы подключены к базе данных "testdb" как пользователь "testread".
```

выполним select запрос:
```postgresql
testdb=> select * from testnm.t1;
ERROR:  permission denied for table t1
```

Т.к. таблица пересоздавалась, то права для этой таблицы для пользователя `testread` ещё не заданы.

Перезайдём в БД как пользователь `postgres`:
```postgresql
testdb=> \c - postgres

Вы подключены к базе данных "testdb" как пользователь "postgres".
```

Добавим права на "новые объекты":
```postgresql
ALTER DEFAULT PRIVILEGES IN SCHEMA testnm GRANT SELECT ON TABLES TO readonly; 
```

ALTER DEFAULT PRIVILEGES позволяет задавать права, применяемые к объектам, 
которые будут создаваться в будущем. Эта команда не затрагивает права, 
назначенные уже существующим объектам.

Переключимся обратно на пользователя `testread`:
```postgresql
testdb=> \c - testread

Вы подключены к базе данных "testdb" как пользователь "testread".
```

Повторим select запрос:
```postgresql
testdb=> select * from testnm.t1;
ERROR:  permission denied for table t1
```

Получилась такая ситуация: таблица `t1` появилась после назначения прав через `GRANT`, 
но раньше, чем `ALTER DEFAULT PRIVILEGES`. Т.е., чтобы решить текущую проблему, 
надо либо `GRANT` выдать, либо пересоздать таблицу.

Переключимся как пользователь `postgres`:
```postgresql
testdb=> \c - postgres

Вы подключены к базе данных "testdb" как пользователь "postgres".
```

Пересоздадим таблицу: 
```postgresql
drop table testnm.t1;
create table testnm.t1(c1 integer); 
insert into testnm.t1(c1) values(1);
```

Переключимся обратно на пользователя `testread`:
```postgresql
testdb=> \c - testread

Вы подключены к базе данных "testdb" как пользователь "testread".
```

И выполним select запрос:
```postgresql
testdb=> select * from testnm.t1;
 c1 
----
  1
(1 строка)
```

Теперь всё получилось!


Теперь давайте выполним команду создания таблицы и вставки данных 
из-под пользователя `testread`:
```postgresql
testdb=> create table t2(c1 integer); insert into t2 values (2);
CREATE TABLE
INSERT 0 1
```

Эти две команды получилось выполнить, потому что не указана схема. 
Если указать схему6 то получим ошибку в правах:
```postgresql
testdb=> create table testnm.t3(c1 integer);
ERROR:  permission denied for schema testnm
СТРОКА 1: create table testnm.t3(c1 integer);
                       ^
```
Т.е. в public схеме создавать таблицы можем, а в схеме testnm - нет.

Давайте отзовём права у public схемы.

Переключимся как пользователь `postgres`:
```postgresql
testdb=> \c - postgres

Вы подключены к базе данных "testdb" как пользователь "postgres".
```

Удалим права на создание объектов в схеме public 
и удалим все права на БД `testdb` со схемой public:
```postgresql
revoke CREATE on SCHEMA public FROM public; 
revoke all on DATABASE testdb FROM public;
```

Переключимся обратно на пользователя `testread`:
```postgresql
testdb=> \c - testread

Вы подключены к базе данных "testdb" как пользователь "testread".
```

И создадим таблицу t4:
```postgresql
testdb=> create table t4(c1 integer);
ERROR:  permission denied for schema public
СТРОКА 1: create table t4(c1 integer);
                       ^
```

Теперь создать в схему public у пользователя testread не получается 
из-за отсутствия прав на создание объектов.
