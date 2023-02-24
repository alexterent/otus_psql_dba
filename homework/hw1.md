# Домашняя работа 1

В этой работе выполним установку PostgreSQL и сравним два уровня изоляции.

____

### 1. Установка PostgreSQL
Для установки PostgreSQL на CentOS7 для начала нужно отключить репозитории postgresql от Centos:

```shell
sudo vi /etc/yum.repos.d/CentOS-Base.repo
```
и добавить исключение репозиториев posgresql в блоках `[base]` и `[upgrade]`. 
Выглядеть будет примерно следующим образом:

```
[base] name=CentOS-$releasever - Base
...
exclude=postgresql*


[updates] name=CentOS-$releasever - Updates
...
exclude=postgresql*
```

После этих действий нужно добавить официальные репозитории postgresql:
```shell
sudo yum install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
```

и выполним установку postgresql 14 версии:
```shell
sudo yum install postgresql14-server
```

На все запросы импорта GPG ключа отвечаем "yes". 
В конце у вас должно появиться сообщение, что зависимости установлены.

Чтобы проверить, что postgresql установлен, можно посмотреть список установленных пакетов:
```shell
$ yum list installed | grep postgres
postgresql14.x86_64                   14.6-1PGDG.rhel7              @pgdg14     
postgresql14-libs.x86_64              14.6-1PGDG.rhel7              @pgdg14     
postgresql14-server.x86_64            14.6-1PGDG.rhel7              @pgdg14 
```

Добавим службу postgresql в автозагрузку:
```shell
sudo systemctl enable postgresql-14
```

После этой команды можно будет запускать и останавливать службу при помощи команд:
```shell
sudo systemctl start postgresql-14
sudo systemctl stop postgresql-14
```


### 2. Создание базы данных и настройка подключения

Создадим кластер 
```shell
$ sudo /usr/pgsql-14/bin/postgresql-14-setup initdb
Initializing database ... OK
```

Подправим `pg_hba.conf` и `postgresql.conf`. Чтобы найти, где расположены эти файлы, 
выполним запрос:
```shell
sudo ps aux  | grep 'postmaster'
```

В выводе необходимо найти путь до папки data, в моём случае это `/var/lib/pgsql/14/data/`.

Далее изменим файл `pg_hba.conf` и добавим следующую строчку:
```
host	all		homework1,homework2,homework3,homework4		0.0.0.0/0		scram-sha-256
```

А в `postgresql.conf` расскомментируем параметр `listen_addresses` и заменим значение:
```
listen_addresses = '*'
```
Для того, чтобы postgresql слушал все ip на дефолтном порту (5432).

Сделаем рестарт, чтобы значения применились:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

После этих дейтсвий мы можем подключиться за пользователя postgres и перейти в консоль psql.


### 3. Исследование транзакций - вставка данных из-под разных сессий, select, auto commit

Переключимся из-под пользователя homework1 на postgres:
```shell
sudo su - postgres
psql
```

И тоже самое сделаем из-под пользователя homework2.

Далее отключим autocommit из **первой сессии** (homework1):
```postgresql
postgres=# \set AUTOCOMMIT OFF
postgres=# \echo :AUTOCOMMIT
OFF
```


> Обратите внимание, что во второй сессии (homework2) autocommit включен:
> ```postgresql
> postgres=# \echo :AUTOCOMMIT
> on
> ```

Создадим в **первой сессии** таблицу и наполним её данными:
```postgresql
create table persons(id serial, first_name text, second_name text); 
insert into persons(first_name, second_name) values('ivan', 'ivanov'); 
insert into persons(first_name, second_name) values('petr', 'petrov'); 
commit;
```

По итогу должна создаться таблица `persons` с двумя записями. 

Теперь посмотрим текущий уровень изоляции в **первой сессии**:
```postgresql
postgres=# show transaction isolation level;
 transaction_isolation 
-----------------------
 read committed
(1 row)
```

Теперь откроем транзакцию в обоих сессиях:
```postgresql
BEGIN;
```

И добавим новую запись в **первой сессии**: 
```postgresql
insert into persons(first_name, second_name) values('sergey', 'sergeev');
```

Не завершая транзакцию, перейдём во **вторую сессию** и посмотрим, какие данные 
сейчас доступны в таблице `person`:
```postgresql
postgres=*# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
(2 rows)
```

Новая запись "sergey sergeev" не появилась во второй сессии, т.к. транзакция из первой сессии 
ещё не завершена и не сохранена, а автокоммит отключен.
Чтобы данные сохранились, необходимо вручную написать `commit`.

Завершим и сохраним транзакцию в **первой сессии**: 
```postgresql
commit;
```

Повторим select во **второй сессии**: 
```postgresql
postgres=*# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
  3 | sergey     | sergeev
(3 rows)
```

Теперь новая строчка отображается во второй сессии. Но важно учитывать ещё один фактор: 
сейчас транзакция находится в Read committed (Чтение зафиксированных данных), поэтому ей 
доступно неповторяемое чтение данных, т.е. чтение данных, которые были изменены в другой транзакции. 
Если бы во второй сессии был бы другой уровень транзакции, например, Repeatable read, то данные не отобразились бы.
Давайте это посмотрим на примере.

Завершим транзакцию во **второй сессии**:
```postgresql
END;
```

Начнём новые транзакции в **обоих сессиях** с другим уровнем транзакции:
```postgresql
BEGIN;
set transaction isolation level repeatable read;
```

И добавим ещё одну строку в **первой сессии**:
```postgresql
insert into persons(first_name, second_name) values('sveta', 'svetova');
```

Посмотрим, что в таблице `persons` во **второй сессии**:
```postgresql
postgres=*# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
  3 | sergey     | sergeev
(3 rows)
```

Новой записи не появилось, что вполне ожидаемо, ведь первая транзакция не была сохранена, 
а значит её изменения изолированны для доступа других транзакций (как и в первом случае).

Теперь завершим транзакцию в **первой сессии**: 
```postgresql
commit;
```

И снова посмотрим что в таблице `persons` во **второй сессии**:
```postgresql
postgres=*# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
  3 | sergey     | sergeev
(3 rows)
```

Новая запись не появилась. В этом примере уровень транзакции был изменён, и на этом 
уровне (Repeatable read) невозможно повторное чтение данных, как это было в предыдущем уровне изоляции.
Т.е. в режиме Repeatable Read видны только те данные, которые были зафиксированы до начала транзакции.

Завершим вторую транзакцию и посмотрим ещё раз - изменились данные или нет. 
```postgresql
postgres=*# commit;
COMMIT
postgres=# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
  3 | sergey     | sergeev
  4 | sveta      | svetova
(4 rows)
```

Когда мы завершили транзакцию, то уровень транзакции, на котором был выполнен select 
был Read committed, поэтому новые данные отобразились.
