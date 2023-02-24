# Домашняя работа 2

В этой работе проведём установку и настройку PostgteSQL в контейнере Docker

____

### 1. Установка Docker

Перед началом установки docker необходимо обновить пакеты:
```shell
sudo yum check-update
```

Далее установим необходимые пакеты для работы с docker: 
```shell
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
```

Добавим репозиторий docker в yum:
```shell
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

И установим docker:
```shell
sudo yum install -y docker-ce
```

Для запуска docker от другого пользователя, необходимо добавить пользователя в группу:
```shell
sudo usermod -aG docker homework1
```

Запустим docker на ВМ:
И установим docker:
```shell
sudo systemctl start docker
```

И проверим, что docker работает:
```shell
$ sudo docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```


### 2. Установка PostgreSQL в Docker и подключение к БД

Для начала создадим свою docker-network:
```shell
sudo docker network create pg-net
```

И проверим, что сеть создалась: 
```shell
$ sudo docker network ls
NETWORK ID     NAME      DRIVER    SCOPE
194591ba21d4   bridge    bridge    local
6f716d1eacbe   host      host      local
afe63489abb3   none      null      local
f30a44e0d037   pg-net    bridge    local
```
Это понадобится для того, чтобы контейнеры могли общаться и взаимодействовать 
в одной изолированной сети.


Создадим каталог `/var/lib/mypostgres`
```shell
sudo mkdir /var/lib/mypostgres
```

Скачаем образ PostgreSQL:
```shell
sudo docker pull postgres:14
```

И посмотрим, что новый image есть в списке доступных image для docker:
```shell
$ sudo docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED      SIZE
postgres     14        9316bd7ca2d7   4 days ago   376MB
```

Для запуска контейнера необходимо написать: 
```shell
sudo docker container run --name pg-server --network pg-net -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 -v /var/lib/mypostgres:/var/lib/postgresql/data --rm 9316bd7ca2d7
```
`--name` - имя контейнера.
`--network` - сеть, в которой будет работать контейнер.
`-e` - установка переменной окружения.
`-d` - запускает контейнер в фоновом режиме.
`-p` - порт, по которому будет происходить взаимодействие с контейнером. В данном случае внутренний и внешний порты совпадают.
`-v` - создание и привязка вольюма для контейнера, где будут храниться данные PosgreSQL.
`--rm` - автоматически удаляет контейнер после того, как его выполнение завершится.
`image_id` - id image, из которого будет создан контейнер. 

Посмотреть запущенный контейнер можно при помощи команды `docker ps`:
```shell
$ sudo docker ps -a
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS         PORTS                                       NAMES
5e4a48e6e49b   9316bd7ca2d7   "docker-entrypoint.s…"   8 seconds ago    Up 7 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   pg-server
```

Развернём ещё один контейнер с клиентом postgresql и сразу же подключимся к postgres-серверу:
```shell
sudo docker run -it --rm --network pg-net --name pg-client 9316bd7ca2d7 psql -h pg-server -U postgres
```

Из-под **клиента** создадим таблицу и несколько записей: 
```postgresql
create table persons(id serial, first_name text, second_name text); 
insert into persons(first_name, second_name) values('ivan', 'ivanov'); 
insert into persons(first_name, second_name) values('petr', 'petrov');
```

Проверим, что та блица создалась:
```postgresql
postgres# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
(2 rows)
```

Подключимся к серверу с ВМ с homework1:
Для этого перейдём в интерактивный режим postgres-server контейнера:
```shell
sudo docker exec -it 5e4a48e6e49b bash
```

И установим редактор nano:
```shell
apt update
apt install nano
```

А затем отредактируем файл `pg_hba.conf`:
```shell
nano /var/lib/postgresql/data/pg_hba.conf
```
И добавим строчку `host all postgres 0.0.0.0/0 scram-sha-256`.

Далее на ВМ пробуем подключиться к БД:
```shell
$ psql -h localhost -U postgres -d postgres
Пароль пользователя postgres: 
psql (14.6)
Введите "help", чтобы получить справку.
```

После успешного подключения, проверяем данные из таблицы `persons`:
```postgresql
postgres# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
(2 строки)
```

Для проверки работы вольюма, нужно выключить контейнер. 
Убедимся, что он всё ещё запущен и работает:
```shell
$sudo docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS                                       NAMES
5e4a48e6e49b   9316bd7ca2d7   "docker-entrypoint.s…"   2 hours ago   Up 2 hours   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   pg-server
````
И остановим контейнер:
```shell
$ sudo docker container stop 5e4a48e6e49b
5e4a48e6e49b
```
Т.к. при запуске контейнера был указан ключ `--rm`, то после остановки контейнер удалится.

Для проверки того, что контейнер удалён, запустим команду `ps` с ключом `-a`
```shell
$ sudo docker ps -a
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS    PORTS     NAMES
```

Контейнер отсутствует.

Далее запустим новый контейнер (строка ничем не отличается от первого запуска):
```shell
sudo docker container run --name pg-server --network pg-net -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 -v /var/lib/mypostgres:/var/lib/postgresql/data --rm 9316bd7ca2d7
```

И убедимся, что это другой контейнер, т.к. новый контейнер будет иметь другой `containet_id`:
```shell
$ sudo docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                       NAMES
1f299ab89d2d   9316bd7ca2d7   "docker-entrypoint.s…"   15 seconds ago   Up 14 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   pg-server
```

Подключимся из-под контейнера для клиента:
```shell
sudo docker run -it --rm --network pg-net --name pg-client 9316bd7ca2d7 psql -h pg-server -U postgres
```

И выполним select запрос:
```postgresql
postgres=# select * from persons;
 id | first_name | second_name 
----+------------+-------------
  1 | ivan       | ivanov
  2 | petr       | petrov
(2 rows)
```

Данные остались прежними, а это значит, что данные были сохранены в docker volume. 