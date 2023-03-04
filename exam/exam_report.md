# Проектная работа

Проектная работа: "Сравнение работы PostgreSQL кластера в зависимости от различных настроек 
и оптимизации запросов на различных массивах данных"

____

## Оглавление

1. [О проекте](#о-проекте)
2. [Подготовительная работа](#подготовительная-работа)
   1. [Установка окружения](#установка-окружения)
   2. [Подготовка pgbench](#подготовка-pgbench)
3. [Эксперименты](#эксперименты)
   1. [Эксперимент №1](#эксперимент-1)
   2. [Эксперимент №2](#эксперимент-2)
   3. [Оценка времени между 1 и 2 экспериментами](#оценка-времени-между-1-и-2-экспериментами)
   4. [Эксперимент №3](#эксперимент-3)
   5. [Эксперимент №4](#эксперимент-4)
   6. [Эксперимент №5](#эксперимент-5)
   7. [Эксперимент №6](#эксперимент-6)
   8. [Промежуточный запуск после эксперимента №6](#промежуточный-запуск-после-эксперимента-6)
   9. [Оценка времени между 2 и 6 экспериментами](#оценка-времени-между-2-и-6-экспериментами)
   10. [Эксперимент №7](#эксперимент-7)
   11. [Оценка времени между 2 и 7 экспериментами](#оценка-времени-между-2-и-7-экспериментами)
   12. [Эксперимент №8](#эксперимент-8)
   13. [Оценка времени между 7 и 8 экспериментами](#оценка-времени-между-7-и-8-экспериментами)
   14. [Эксперимент №9](#эксперимент-9)
   15. [Оценка времени между 1 и 9 экспериментами](#оценка-времени-между-1-и-9-экспериментами)
   16. [Эксперимент №10](#эксперимент-10)
   17. [Оценка времени между 2 и 10 экспериментами](#оценка-времени-между-2-и-10-экспериментами)
   18. [Эксперимент №11](#эксперимент-11)
   19. [Оценка времени между 7 и 11 экспериментами](#оценка-времени-между-7-и-11-экспериментами)
   20. [Эксперимент №12](#эксперимент-12)
   21. [Оценка времени между 11 и 12 экспериментами](#оценка-времени-между-11-и-12-экспериментами)
   22. [Эксперимент №13](#эксперимент-13)
   23. [Оценка времени между 8 и 13 экспериментами](#оценка-времени-между-8-и-13-экспериментами)
   24. [Оценка времени между 9 и 13 экспериментами](#оценка-времени-между-9-и-13-экспериментами)
   25. [Оценка времени между 1 и 13 экспериментами](#оценка-времени-между-1-и-13-экспериментами)
   26. [Эксперимент №14](#эксперимент-14)
   27. [Эксперимент №15](#эксперимент-15)
   28. [Оценка времени между 2 и 14 экспериментами](#оценка-времени-между-2-и-14-экспериментами)
   29. [Оценка времени между 10 и 15 экспериментами](#оценка-времени-между-10-и-15-экспериментами)
   30. [Оценка времени между 14 и 15 экспериментами](#оценка-времени-между-14-и-15-экспериментами)
4. [Выводы](#выводы)

____


## О проекте

Существует 4 способа улучшить производительность:
1. Настройка конфигурации PostgreSQL
2. Индексы
3. Изменить SQL-запрос
4. Изменить хост (CPU, RAM, Disk type)

В этой работе будет проведён анализ при помощи pgbench с различных настроек в postgresql.conf на ВМ с HDD диском.
А затем проведена проверка как будет работать кластер на SSD диске с такими же настройками как для HDD.

Основные цели эксперимента:
1. Получить максимальное среднее tcp;
2. Получить минимальное среднее latency.

## Подготовительная работа

### Установка окружения


Создадим ВМ с 8 CPU, 16 RAM, HDD 20 Gb. Установим CentOS 7.
И создадим вторую такую же машину, только с SSD диском. Все подготовительные шаги также повторим на ней.

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


Добавим службу postgresql в автозагрузку:
```shell
sudo systemctl enable postgresql-14
```

Создадим кластер 
```shell
$ sudo /usr/pgsql-14/bin/postgresql-14-setup initdb
Initializing database ... OK
```

В выводе необходимо найти путь до папки data, в моём случае это `/var/lib/pgsql/14/data/`.

Далее изменим файл `pg_hba.conf` и добавим следующую строчку:
```
host	all		homework		0.0.0.0/0		scram-sha-256
```

И подправить настройки для подключения postgres пользователя с local для `pgbench`:
```
local   all             postgres                                peer
```
на 
```
local   all             postgres                                trust
```

Cоздадим директорию `conf.d` в `/var/lib/pgsql/14/data` для изменённых конфигураций:
```shell
$ sudo mkdir /var/lib/pgsql/14/data/conf.d/
```

В `postgresql.conf` расскомментируем параметр `listen_addresses` и заменим значение:
```
listen_addresses = '*'
```

Расскомментируем строчку с настройкой: 
```
unix_socket_directories = '/var/run/postgresql/, /tmp'
```

И добавим директорию для конфигураций в конце: 
```
include_dir = 'conf.d'
```

Для того, чтобы запустить `pgbench`, необходимо установить contrib:
```shell
sudo yum install postgresql-contrib
```

Сделаем рестарт, чтобы значения применились:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```


### Подготовка pgbench

Создадим БД для тестирования 
(`testdb1`, `testdb2`, `testdb3`, `testdb4`, `testdb5`, `testdb6`, `testdb7`) pgbench. 
Описание этих БД находится в файле [create_DBs](/exam/create_db.sql).

Для экспериментов будут использоваться таблицы с разным кол-вом данных `-s` (1, 10, 100), 
партиционированием (для s=10 partitions=10, для s=100 partitions=20) и для s=100 будет использован ключ 
для нежурналируемых таблиц `unlogged-table`.

Создадим таблицы для тестирования в pgbench.
```shell
sudo /usr/pgsql-14/bin/pgbench -i -U postgres {OTHER-PARAMS} testdb{NUMBER}
```
Инициализация таблиц для ВМ с HDD представлена в [init_tables_hdd](/exam/init_tables_hdd.md).
Инициализация таблиц для ВМ с SSD представлена в [init_tables_ssd](/exam/init_tables_ssd.md).

При просмотре времени на создание таблиц, был обнаружено, что создание таблицы с параметрами `-s 100 --unlogged-tables` 
было самым быстрым из всех 4-х таблиц с параметром s=100. 

**Можно выдвинуть гипотезу**, что результаты по testdb6 будут самыми быстрыми среди testdb4, testdb5, testdb6, testdb7, 
потому что таблицы там нежурналируемые и нет партиций.


В каждой БД запустим update таблицы `pgbench_branches`.
```postgresql
UPDATE pgbench_branches SET bbalance=4500000 WHERE bid % 3 = 0;
```

Для таблицы s=1 будет 0 изменений.
Для таблиц s=10 будет 3 изменения.
Для таблиц s=100 будет 33 изменения.


Создадим на ВМ файл для custom select и скопируем туда кастомный SQL запрос [custom select](/exam/custom_select.sql):
```shell
sudo touch /tmp/custom_select.sql
sudo vi /tmp/custom_select.sql
```


## Эксперименты

Эксперименты запускаются на 3 разных объёмах таблиц pgbench
с различными тестами: custom select with join, simple и extended тесты.

Запуск по 30 секунд, с 5, 50 и 200 клиентами.


Ключи, используемые в запуске эксперимента:
-c - Число одновременных сеансов базы данных
-f - Добавить в список выполняемых скриптов скрипт транзакции из файла
-j - Число рабочих потоков в pgbench
-M - Протокол, выбираемый для передачи запросов на сервер. Simple (по умолчанию) или extended
-U - Пользователь для подключения к БД
-P - Выводить отчёт о прогрессе через заданное число секунд
-T - Выполнять тест с ограничением по времени (в секундах), а не по числу транзакций для каждого клиента
-r - Выводить по завершении тестировании средняя время ожидания операторов (время выполнения с точки зрения клиента) для каждой команды


Bash скрипт для запуска эксперимента можно посмотреть в файле [run_exp](/exam/run_exp.sh).

На ВМ создадим файл, скопируем туда этот файл и добавим права на исполняемый скрипт:
```shell
sudo touch /tmp/run_exp.sh
sudo vi /tmp/run_exp.sh
sudo chmod +x /tmp/run_exp.sh
```

Конфигурации, на которых проводились тесты представлены в файле [Конфигурации БД](/exam/configs.md)

В ходе эксперимента, попробуем проследить, насколько сильно зависят средние TPS и latencies от кол-ва клиентов, 
объёма данных, партиционирования и журналирования. 


Результаты эксперимента и получение итоговой таблицы обрабатывались с помощью python скрипта в файле [for_exp.py](/exam/for_exp.py).


### Эксперимент №1

**Эксперимент:** запуск на дефолтных параметрах PostgreSQL.

<details>
<summary>-M = simple</summary>

|         | c = 5                                      | c = 50                                      | c = 200                              |
|---------|--------------------------------------------|---------------------------------------------|--------------------------------------|
| testdb1 | latency = 7.818 ms <br/> tps = 639.429776  | latency = 78.946 ms <br/> tps = 632.030684  | latency = error ms <br/> tps = error |
| testdb2 | latency = 6.980 ms <br/> tps = 715.933164  | latency = 30.162 ms <br/> tps = 1655.474634 | latency = error ms <br/> tps = error |
| testdb3 | latency = 5.503 ms <br/> tps = 907.811767  | latency = 30.891 ms <br/> tps = 1614.835521 | latency = error ms <br/> tps = error |
| testdb4 | latency = 7.027 ms <br/> tps = 711.006122  | latency = 32.663 ms <br/> tps = 1528.466675 | latency = error ms <br/> tps = error |
| testdb5 | latency = 14.104 ms <br/> tps = 353.912548 | latency = 176.134 ms <br/> tps = 281.130779 | latency = error ms <br/> tps = error |
| testdb6 | latency = 0.562 ms <br/> tps = 8871.772535 | latency = 6.712 ms <br/> tps = 7419.898820  | latency = error ms <br/> tps = error |
| testdb7 | latency = 0.729 ms <br/> tps = 6842.112984 | latency = 7.349 ms <br/> tps = 6775.441528  | latency = error ms <br/> tps = error |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                              |
|---------|--------------------------------------------|---------------------------------------------|--------------------------------------|
| testdb1 | latency = 7.557 ms <br/> tps = 661.521029  | latency = 78.175 ms <br/> tps = 638.612099  | latency = error ms <br/> tps = error |
| testdb2 | latency = 6.072 ms <br/> tps = 822.915378  | latency = 39.301 ms <br/> tps = 1269.716772 | latency = error ms <br/> tps = error |
| testdb3 | latency = 5.857 ms <br/> tps = 853.151768  | latency = 38.481 ms <br/> tps = 1297.846964 | latency = error ms <br/> tps = error |
| testdb4 | latency = 9.171 ms <br/> tps = 544.891814  | latency = 140.724 ms <br/> tps = 346.751488 | latency = error ms <br/> tps = error |
| testdb5 | latency = 21.641 ms <br/> tps = 230.882821 | latency = 142.629 ms <br/> tps = 337.648139 | latency = error ms <br/> tps = error |
| testdb6 | latency = 0.839 ms <br/> tps = 5945.654694 | latency = 7.387 ms <br/> tps = 6742.503819  | latency = error ms <br/> tps = error |
| testdb7 | latency = 0.842 ms <br/> tps = 5923.596672 | latency = 6.880 ms <br/> tps = 6742.426660  | latency = error ms <br/> tps = error |

</details>


<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                       | c = 50                                      |
|---------|---------------------------------------------|---------------------------------------------|
| testdb1 | latency = 58.943 ms <br/> tps = 84.778559   | latency = 532.426 ms <br/> tps = 93.631536  |
| testdb2 | latency = 552.708 ms <br/> tps = 9.011734   | latency = 5311.915 ms <br/> tps = 9.087683  |
| testdb3 | latency = 617.786 ms <br/> tps = 8.048790   | latency = 5348.107 ms <br/> tps = 8.972057  |
| testdb4 | latency = 5347.688 ms <br/> tps = 0.917142  | latency = 52163.638 ms <br/> tps = 0.930169 |
| testdb5 | latency = 10233.672 ms <br/> tps = 0.480714 | latency = 53008.420 ms <br/> tps = 0.907886 |
| testdb6 | latency = 5327.363 ms <br/> tps = 0.907694  | latency = 56768.138 ms <br/> tps = 0.851059 |
| testdb7 | latency = 5723.997 ms <br/> tps = 0.856605  | latency = 53788.133 ms <br/> tps = 0.884423 |

</details>

Полный отчет тестов представлен в файле [experiment 1](/exam/experiments/e_1.md).


**Наблюдение:** без дополнительных настроек или указания дополнительных ключей, хеширования или иного, 
чтение sql функции из файла для `-f` очень медленное, и чем больше таблицы `-s`, тем больше значение `latency`.

Из тестов были исключены с = 200 для `-f`, т.к. это приводило к очень большим `latency`.


### Эксперимент №2

Эксперимент: улучшить конфигурацию кластера при помощи pgtune.

Задаим конфигурацию кластера в pgtune и сгенерируем конфиг для:
```
DB Version: 14
OS Type: linux
DB Type: oltp
Total Memory (RAM): 16 GB
CPUs num: 8
Connections num: 1000
Data Storage: hdd
```

Полученный конфиг для данной конфигурации запишем в файл `pgtune.conf`:
```shell
sudo touch /var/lib/pgsql/14/data/conf.d/pgtune.conf
sudo vi /var/lib/pgsql/14/data/conf.d/pgtune.conf
```

Полный конфиг файла `pgtune.conf` можно посмотреть в [Конфигуарция для эксперимента №2](/exam/configs.md#конфигуарция-для-эксперимента-2)

Сделаем рестарт, чтобы значения применились:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 7.578 ms <br/> tps = 659.641665  | latency = 75.926 ms <br/> tps = 657.562027  | latency = 388.284 ms <br/> tps = 512.041007  |
| testdb2 | latency = 4.153 ms <br/> tps = 1202.830977 | latency = 22.889 ms <br/> tps = 2179.325500 | latency = 76.009 ms <br/> tps = 2623.784600  |
| testdb3 | latency = 4.364 ms <br/> tps = 1144.802765 | latency = 23.057 ms <br/> tps = 2164.839018 | latency = 77.311 ms <br/> tps = 2577.692134  |
| testdb4 | latency = 3.913 ms <br/> tps = 1276.257340 | latency = 12.239 ms <br/> tps = 4070.278393 | latency = 53.875 ms <br/> tps = 3694.330168  |
| testdb5 | latency = 12.565 ms <br/> tps = 397.732243 | latency = 20.386 ms <br/> tps = 2439.598260 | latency = 5937.676 ms <br/> tps = 28.796698  |
| testdb6 | latency = 6.029 ms <br/> tps = 829.028256  | latency = 5.090 ms <br/> tps = 9763.862384  | latency = 18.914 ms <br/> tps = 10472.201735 |
| testdb7 | latency = 0.543 ms <br/> tps = 9169.433404 | latency = 3.939 ms <br/> tps = 12583.674270 | latency = 19.721 ms <br/> tps = 10049.008573 |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                     |
|---------|--------------------------------------------|---------------------------------------------|---------------------------------------------|
| testdb1 | latency = 7.471 ms <br/> tps = 669.026763  | latency = 80.146 ms <br/> tps = 623.046237  | latency = 462.340 ms <br/> tps = 429.735615 |
| testdb2 | latency = 3.897 ms <br/> tps = 1281.808014 | latency = 18.548 ms <br/> tps = 2691.310144 | latency = 75.072 ms <br/> tps = 2655.841791 |
| testdb3 | latency = 4.283 ms <br/> tps = 1166.303442 | latency = 21.259 ms <br/> tps = 2347.784839 | latency = 76.295 ms <br/> tps = 2606.766114 |
| testdb4 | latency = 4.170 ms <br/> tps = 1197.444452 | latency = 14.205 ms <br/> tps = 3277.820955 | latency = 46.155 ms <br/> tps = 4308.833937 |
| testdb5 | latency = 12.042 ms <br/> tps = 414.965175 | latency = 30.029 ms <br/> tps = 1661.614241 | latency = 4161.817 ms <br/> tps = 44.237328 |
| testdb6 | latency = 0.757 ms <br/> tps = 6589.787645 | latency = 4.979 ms <br/> tps = 9975.221444  | latency = 20.367 ms <br/> tps = 9732.198566 |
| testdb7 | latency = 0.624 ms <br/> tps = 7983.621631 | latency = 4.735 ms <br/> tps = 10476.953176 | latency = 22.970 ms <br/> tps = 8624.853564 |

</details>


<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                       | c = 50                                      |
|---------|---------------------------------------------|---------------------------------------------|
| testdb1 | latency = 59.607 ms <br/> tps = 83.813968   | latency = 544.667 ms <br/> tps = 91.397018  |
| testdb2 | latency = 574.772 ms <br/> tps = 8.642348   | latency = 4984.548 ms <br/> tps = 9.823204  |
| testdb3 | latency = 607.732 ms <br/> tps = 8.197381   | latency = 5526.516 ms <br/> tps = 8.896585  |
| testdb4 | latency = 6332.058 ms <br/> tps = 0.749280  | latency = 79513.157 ms <br/> tps = 0.614868 |
| testdb5 | latency = 32666.364 ms <br/> tps = 0.145837 | latency = 55600.417 ms <br/> tps = 0.862084 |
| testdb6 | latency = 5645.428 ms <br/> tps = 0.860620  | latency = 50693.187 ms <br/> tps = 0.955225 |
| testdb7 | latency = 5811.131 ms <br/> tps = 0.819086  | latency = 55666.469 ms <br/> tps = 0.873296 |

</details>

Полный отчет тестов представлен в файле [experiment 2](/exam/experiments/e_2.md).



### Оценка времени между 1 и 2 экспериментами

При помощи скрипта [for_exp.py](/exam/for_exp.py) построим сравнительные таблицы между двумя результатами:

-M = simple

|         | c = 5                                          | c = 50                                           | c = 200         |
|---------|------------------------------------------------|--------------------------------------------------|-----------------|
| testdb1 | latency = - 0.24 ms <br/> tps = + 20.211889    | latency = - 3.02 ms <br/> tps = + 25.531343      | Can't calculate |
| testdb2 | latency = - 2.827 ms <br/> tps = + 486.897813  | latency = - 7.273 ms <br/> tps = + 523.850866    | Can't calculate |
| testdb3 | latency = - 1.139 ms <br/> tps = + 236.990998  | latency = - 7.834 ms <br/> tps = + 550.003497    | Can't calculate |
| testdb4 | latency = - 3.114 ms <br/> tps = + 565.251218  | latency = - 20.424 ms <br/> tps = + 2541.811718  | Can't calculate |
| testdb5 | latency = - 1.539 ms <br/> tps = + 43.819695   | latency = - 155.748 ms <br/> tps = + 2158.467481 | Can't calculate |
| testdb6 | latency = + 5.467 ms <br/> tps = - 8042.744279 | latency = - 1.622 ms <br/> tps = + 2343.963564   | Can't calculate |
| testdb7 | latency = - 0.186 ms <br/> tps = + 2327.32042  | latency = - 3.41 ms <br/> tps = + 5808.232742    | Can't calculate |

В случае простого теста, можно заметить, что лучший прирост среди Б4 4-7 (s=100) показали 4 и 5 по `latency` значению.
Для с = 5 у testdb6 наблюдалось ухудшение значений. Можно сделать несколько предположений, одно из них: 
у ВМ в яндекс облаке были просадки, поэтому можно конкретное значение перезапустить для пересчёта.


-M = extended

|         | c = 5                                          | c = 50                                           | c = 200         |
|---------|------------------------------------------------|--------------------------------------------------|-----------------|
| testdb1 | latency = - 0.086 ms <br/> tps = + 7.505734    | latency = + 1.971 ms <br/> tps = - 15.565862     | Can't calculate |
| testdb2 | latency = - 2.175 ms <br/> tps = + 458.892636  | latency = - 20.753 ms <br/> tps = + 1421.593372  | Can't calculate |
| testdb3 | latency = - 1.574 ms <br/> tps = + 313.151674  | latency = - 17.222 ms <br/> tps = + 1049.937875  | Can't calculate |
| testdb4 | latency = - 5.001 ms <br/> tps = + 652.552638  | latency = - 126.519 ms <br/> tps = + 2931.069467 | Can't calculate |
| testdb5 | latency = - 9.599 ms <br/> tps = + 184.082354  | latency = - 112.6 ms <br/> tps = + 1323.966102   | Can't calculate |
| testdb6 | latency = - 0.082 ms <br/> tps = + 644.132951  | latency = - 2.408 ms <br/> tps = + 3232.717625   | Can't calculate |
| testdb7 | latency = - 0.218 ms <br/> tps = + 2060.024959 | latency = - 2.145 ms <br/> tps = + 3734.526516   | Can't calculate |



В случае сложного теста также лучший прирост показали БД 4 и 5 среди s=100 по показателю `latency`. 

-f custom_select.sql

|         | c = 5                                           | c = 50                                          |
|---------|-------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = + 0.664 ms <br/> tps = - 0.964591     | latency = + 12.241 ms <br/> tps = - 2.234518    |
| testdb2 | latency = + 22.064 ms <br/> tps = - 0.369386    | latency = - 327.367 ms <br/> tps = + 0.735521   |
| testdb3 | latency = - 10.054 ms <br/> tps = + 0.148591    | latency = + 178.409 ms <br/> tps = - 0.075472   |
| testdb4 | latency = + 984.37 ms <br/> tps = - 0.167862    | latency = + 27349.519 ms <br/> tps = - 0.315301 |
| testdb5 | latency = + 22432.692 ms <br/> tps = - 0.334877 | latency = + 2591.997 ms <br/> tps = - 0.045802  |
| testdb6 | latency = + 318.065 ms <br/> tps = - 0.047074   | latency = - 6074.951 ms <br/> tps = + 0.104166  |
| testdb7 | latency = + 87.134 ms <br/> tps = - 0.037519    | latency = + 1878.336 ms <br/> tps = - 0.011127  |

А вот в случае с чтением запроса из файла только БД 6 показала хороший результат. 


### Эксперимент №3

Так как основная проблема HDD диска в том, что нужно уменьшить количество записи на физический диск, 
то попробуем отключить или изменить некоторые из настроек и посмотреть, какие при этом будут получены результаты.

В файле `pgtune.conf` изменим конфиг:
```
log_min_duration_statement = -1
```
Отключим запись в журнал продолжительность выполнения всех команд, время работы которых не меньше указанного. 

Запуск теста проведём на БД 2:
```shell
sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -U postgres testdb2
```

Полный отчет теста представлен в файле [experiment 3](/exam/experiments/e_3_6.md#тестирование-3).

**Результат:** значение tps немного увеличилось.
latency = 4.003 ms
tps = 1247.744392

### Эксперимент №4

pgtune
`huge_pages = off`

Полный отчет теста представлен в файле [experiment 4](/exam/experiments/e_3_6.md#тестирование-4).

**Результат:** значение tps немного увеличилось.
latency = 3.951 ms
tps = 1264.416512


### Эксперимент №5

```
# - Background Writer -

bgwriter_delay = 1000ms                 # 10-10000ms between rounds
bgwriter_lru_maxpages = 10              # max buffers written/round, 0 disables
bgwriter_lru_multiplier = 1.0           # 0-10.0 multiplier on buffers scanned/round
bgwriter_flush_after = 1024kB           # measured in pages, 0 disables
```

Полный отчет теста представлен в файле [experiment 5](/exam/experiments/e_3_6.md#тестирование-5).

**Результат:** значение tps немного увеличилось.
latency = 3.833 ms
tps = 1303.319692


### Эксперимент №6

pgtune
`random_page_cost = 1.0`

Наблюдение, время не изменилось, но значения стали ровнее (стабильнее)

Полный отчет теста представлен в файле [experiment 6](/exam/experiments/e_3_6.md#тестирование-6).

**Результат:** значение tps и latency практически никак не изменилось.
latency = 3.828 ms
tps = 1304.897303
Но промежуточные значения, получаемые с шагом в 10s стали более ровными и близкими по значению друг к другу.


### Промежуточный запуск после эксперимента №6

Запустим все тесты, чтобы посмотреть, как на остальных таблицах отразились изменения конфигурации PostgreSQL.

<details>
<summary>-M = simple</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 6.965 ms <br/> tps = 717.753903  | latency = 83.354 ms <br/> tps = 598.495729  | latency = 582.936 ms <br/> tps = 337.325385  |
| testdb2 | latency = 8.459 ms <br/> tps = 590.678164  | latency = 34.267 ms <br/> tps = 1455.962956 | latency = 124.753 ms <br/> tps = 1596.578152 |
| testdb3 | latency = 8.435 ms <br/> tps = 592.371236  | latency = 33.316 ms <br/> tps = 1498.178988 | latency = 140.362 ms <br/> tps = 1417.722352 |
| testdb4 | latency = 7.874 ms <br/> tps = 634.492534  | latency = 15.140 ms <br/> tps = 3291.479833 | latency = 28.936 ms <br/> tps = 6862.467962  |
| testdb5 | latency = 8.123 ms <br/> tps = 615.038828  | latency = 25.256 ms <br/> tps = 1975.161462 | latency = 229.191 ms <br/> tps = 684.229840  |
| testdb6 | latency = 0.505 ms <br/> tps = 9846.260598 | latency = 18.262 ms <br/> tps = 2731.837323 | latency = 17.085 ms <br/> tps = 11588.312226 |
| testdb7 | latency = 0.545 ms <br/> tps = 9141.548621 | latency = 3.983 ms <br/> tps = 12449.560407 | latency = 19.178 ms <br/> tps = 10337.871945 |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 7.314 ms <br/> tps = 683.299449  | latency = 89.972 ms <br/> tps = 554.328808  | latency = 629.474 ms <br/> tps = 315.366174  |
| testdb2 | latency = 7.982 ms <br/> tps = 626.051767  | latency = 38.264 ms <br/> tps = 1304.493497 | latency = 143.874 ms <br/> tps = 1383.153990 |
| testdb3 | latency = 8.751 ms <br/> tps = 571.021037  | latency = 39.047 ms <br/> tps = 1278.672072 | latency = 163.227 ms <br/> tps = 1216.945901 |
| testdb4 | latency = 7.877 ms <br/> tps = 634.184467  | latency = 17.123 ms <br/> tps = 2912.001594 | latency = 31.266 ms <br/> tps = 6352.153709  |
| testdb5 | latency = 9.356 ms <br/> tps = 534.043453  | latency = 28.430 ms <br/> tps = 1755.366186 | latency = 82.130 ms <br/> tps = 2422.416608  |
| testdb6 | latency = 0.577 ms <br/> tps = 8636.188506 | latency = 4.235 ms <br/> tps = 11707.112856 | latency = 20.241 ms <br/> tps = 9793.638332  |
| testdb7 | latency = 0.626 ms <br/> tps = 7957.120145 | latency = 4.817 ms <br/> tps = 10300.528931 | latency = 22.270 ms <br/> tps = 8902.146781  |

</details>


<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                       | c = 50                                      |
|---------|---------------------------------------------|---------------------------------------------|
| testdb1 | latency = 59.126 ms <br/> tps = 84.528606   | latency = 540.925 ms <br/> tps = 92.120281  |
| testdb2 | latency = 530.691 ms <br/> tps = 9.388367   | latency = 4819.817 ms <br/> tps = 10.156367 |
| testdb3 | latency = 623.130 ms <br/> tps = 7.981235   | latency = 5459.031 ms <br/> tps = 8.912686  |
| testdb4 | latency = 51839.373 ms <br/> tps = 0.093920 | latency = 50298.008 ms <br/> tps = 0.976773 |
| testdb5 | latency = 5688.434 ms <br/> tps = 0.846883  | latency = 52968.908 ms <br/> tps = 0.908565 |
| testdb6 | latency = 5399.748 ms <br/> tps = 0.899987  | latency = 51088.198 ms <br/> tps = 0.946635 |
| testdb7 | latency = 5791.084 ms <br/> tps = 0.835730  | latency = 55642.330 ms <br/> tps = 0.874077 |

</details>

Полный отчет тестов представлен в файле [experiment 6_2](/exam/experiments/e_6_2.md).


### Оценка времени между 2 и 6 экспериментами

При помощи скрипта [for_exp.py](/exam/for_exp.py) построим сравнительные таблицы между двумя результатами:

-M = simple

|         | c = 5                                          | c = 50                                          | c = 200                                          |
|---------|------------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 0.613 ms <br/> tps = + 58.112238   | latency = + 7.428 ms <br/> tps = - 59.066298    | latency = + 194.652 ms <br/> tps = - 174.715622  |
| testdb2 | latency = + 4.306 ms <br/> tps = - 612.152813  | latency = + 11.378 ms <br/> tps = - 723.362544  | latency = + 48.744 ms <br/> tps = - 1027.206448  |
| testdb3 | latency = + 4.071 ms <br/> tps = - 552.431529  | latency = + 10.259 ms <br/> tps = - 666.66003   | latency = + 63.051 ms <br/> tps = - 1159.969782  |
| testdb4 | latency = + 3.961 ms <br/> tps = - 641.764806  | latency = + 2.901 ms <br/> tps = - 778.79856    | latency = - 24.939 ms <br/> tps = + 3168.137794  |
| testdb5 | latency = - 4.442 ms <br/> tps = + 217.306585  | latency = + 4.87 ms <br/> tps = - 464.436798    | latency = - 5708.485 ms <br/> tps = + 655.433142 |
| testdb6 | latency = - 5.524 ms <br/> tps = + 9017.232342 | latency = + 13.172 ms <br/> tps = - 7032.025061 | latency = - 1.829 ms <br/> tps = + 1116.110491   |
| testdb7 | latency = + 0.002 ms <br/> tps = - 27.884783   | latency = + 0.044 ms <br/> tps = - 134.113863   | latency = - 0.543 ms <br/> tps = + 288.863372    |

Лучший результат по уменьшению `latency` показала БД 5 (s=100, partitions=20) с с=200. 

-M = extended

|         | c = 5                                         | c = 50                                          | c = 200                                          |
|---------|-----------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 0.157 ms <br/> tps = + 14.272686  | latency = + 9.826 ms <br/> tps = - 68.717429    | latency = + 167.134 ms <br/> tps = - 114.369441  |
| testdb2 | latency = + 4.085 ms <br/> tps = - 655.756247 | latency = + 19.716 ms <br/> tps = - 1386.816647 | latency = + 68.802 ms <br/> tps = - 1272.687801  |
| testdb3 | latency = + 4.468 ms <br/> tps = - 595.282405 | latency = + 17.788 ms <br/> tps = - 1069.112767 | latency = + 86.932 ms <br/> tps = - 1389.820213  |
| testdb4 | latency = + 3.707 ms <br/> tps = - 563.259985 | latency = + 2.918 ms <br/> tps = - 365.819361   | latency = - 14.889 ms <br/> tps = + 2043.319772  |
| testdb5 | latency = - 2.686 ms <br/> tps = + 119.078278 | latency = - 1.599 ms <br/> tps = + 93.751945    | latency = - 4079.687 ms <br/> tps = + 2378.17928 |
| testdb6 | latency = - 0.18 ms <br/> tps = + 2046.400861 | latency = - 0.744 ms <br/> tps = + 1731.891412  | latency = - 0.126 ms <br/> tps = + 61.439766     |
| testdb7 | latency = + 0.002 ms <br/> tps = - 26.501486  | latency = + 0.082 ms <br/> tps = - 176.424245   | latency = - 0.7 ms <br/> tps = + 277.293217      |

Интересно, что на небольших объёмах данных (s=1, s=10) БД 1-3 показали результаты хуже, чем в эксперименте №2. 
Лучший результат по ускорению работы показала БД 5 (s=100, partitions=20). 
Остальные показали незначительные изменения.


-f custom_select.sql

|         | c = 5                                          | c = 50                                          | 
|---------|------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = - 0.481 ms <br/> tps = + 0.714638    | latency = - 3.742 ms <br/> tps = + 0.723263     |
| testdb2 | latency = - 44.081 ms <br/> tps = + 0.746019   | latency = - 164.731 ms <br/> tps = + 0.333163   |
| testdb3 | latency = + 15.398 ms <br/> tps = - 0.216146   | latency = - 67.485 ms <br/> tps = + 0.016101    |
| testdb4 | latency = + 45507.315 ms <br/> tps = - 0.65536 | latency = - 29215.149 ms <br/> tps = + 0.361905 |
| testdb5 | latency = - 26977.93 ms <br/> tps = + 0.701046 | latency = - 2631.509 ms <br/> tps = + 0.046481  |
| testdb6 | latency = - 245.68 ms <br/> tps = + 0.039367   | latency = + 395.011 ms <br/> tps = - 0.00859    |
| testdb7 | latency = - 20.047 ms <br/> tps = + 0.016644   | latency = - 24.139 ms <br/> tps = + 0.000781    |


Интересно, что в случае с=50 только БД 6 с unlogged table показала самый худший результат. 
Т.е. отключение `huge_pages`, уменьшение значений для bgwriter, и приравнивание random_page_cost=seq_page_cost 
ухудшает работу с нежурналируемаой таблицей.

В целом изменения с 3 по 6 эксперименты ухудшили показатели остальных БД.

**Выводы:** Несмотря на то, что в экспериментах 3-6 показали по БД 2 показатели улучшались за 120с, 
в срезе на 30с показатели 
были ниже между 2 и 6 экспериментами при разных нагрузках. В дальнейших экспериментах эти изменения 
не будут учитываться, конфигурация PostgreSQL вернётся к настройкам после эксперимента №2.


### Эксперимент №7

Уберём все изменения с 3 по 6 эксперимент и добавим настройки по autovacuum в `pgtune.conf`.

Полный конфиг файла `pgtune.conf` можно посмотреть в [Конфигуарция для эксперимента №7](/exam/configs.md#конфигуарция-для-эксперимента-7)

В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 14.684 ms <br/> tps = 340.413331 | latency = 136.000 ms <br/> tps = 366.562718 | latency = 586.591 ms <br/> tps = 337.309155  |
| testdb2 | latency = 8.562 ms <br/> tps = 583.667820  | latency = 34.363 ms <br/> tps = 1452.077498 | latency = 123.679 ms <br/> tps = 1609.030913 |
| testdb3 | latency = 8.515 ms <br/> tps = 586.874451  | latency = 34.005 ms <br/> tps = 1468.403035 | latency = 146.119 ms <br/> tps = 1359.222119 |
| testdb4 | latency = 69.671 ms <br/> tps = 71.748151  | latency = 76.281 ms <br/> tps = 654.196855  | latency = 40.780 ms <br/> tps = 4878.175160  |
| testdb5 | latency = 48.533 ms <br/> tps = 102.996711 | latency = 78.168 ms <br/> tps = 638.558822  | latency = 64.497 ms <br/> tps = 3083.975663  |
| testdb6 | latency = 107.403 ms <br/> tps = 46.477771 | latency = 10.321 ms <br/> tps = 4828.129327 | latency = 18.893 ms <br/> tps = 10491.719400 |
| testdb7 | latency = 31.995 ms <br/> tps = 156.217855 | latency = 3.889 ms <br/> tps = 12746.374602 | latency = 19.031 ms <br/> tps = 10416.148011 |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 15.321 ms <br/> tps = 326.284839 | latency = 158.702 ms <br/> tps = 314.260104 | latency = 644.427 ms <br/> tps = 307.112133  |
| testdb2 | latency = 8.170 ms <br/> tps = 611.589053  | latency = 38.261 ms <br/> tps = 1304.248286 | latency = 138.620 ms <br/> tps = 1434.129693 |
| testdb3 | latency = 8.010 ms <br/> tps = 623.749415  | latency = 37.498 ms <br/> tps = 1331.523662 | latency = 142.419 ms <br/> tps = 1396.245780 |
| testdb4 | latency = 66.183 ms <br/> tps = 75.473893  | latency = 18.914 ms <br/> tps = 2635.965590 | latency = 55.386 ms <br/> tps = 3593.513878  |
| testdb5 | latency = 65.380 ms <br/> tps = 76.372600  | latency = 23.547 ms <br/> tps = 2118.769404 | latency = 91.247 ms <br/> tps = 2182.407713  |
| testdb6 | latency = 110.694 ms <br/> tps = 45.134429 | latency = 5.316 ms <br/> tps = 9345.019145  | latency = 33.168 ms <br/> tps = 5994.815815  |
| testdb7 | latency = 22.875 ms <br/> tps = 218.482064 | latency = 4.603 ms <br/> tps = 10775.719512 | latency = 22.141 ms <br/> tps = 8952.510451  |

</details>


<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                        | c = 50                                      |
|---------|----------------------------------------------|---------------------------------------------|
| testdb1 | latency = 57.995 ms <br/> tps = 86.176575    | latency = 522.694 ms <br/> tps = 95.409299  |
| testdb2 | latency = 539.006 ms <br/> tps = 9.215095    | latency = 4723.109 ms <br/> tps = 10.346743 |
| testdb3 | latency = 592.296 ms <br/> tps = 8.393529    | latency = 5254.511 ms <br/> tps = 9.146049  |
| testdb4 | latency = 190634.394 ms <br/> tps = 0.026165 | latency = 46898.724 ms <br/> tps = 0.987678 |
| testdb5 | latency = 109417.065 ms <br/> tps = 0.044955 | latency = 51693.600 ms <br/> tps = 0.934812 |
| testdb6 | latency = 197523.257 ms <br/> tps = 0.025221 | latency = 50465.258 ms <br/> tps = 0.969213 |
| testdb7 | latency = 52314.502 ms <br/> tps = 0.092177  | latency = 53446.548 ms <br/> tps = 0.910520 |

</details>

Полный отчет тестов представлен в файле [experiment 7](/exam/experiments/e_7.md).



### Оценка времени между 2 и 7 экспериментами

-M = simple

|         | c = 5                                           | c = 50                                          | c = 200                                           |
|---------|-------------------------------------------------|-------------------------------------------------|---------------------------------------------------|
| testdb1 | latency = + 7.106 ms <br/> tps = - 319.228334   | latency = + 60.074 ms <br/> tps = - 290.999309  | latency = + 198.307 ms <br/> tps = - 174.731852   |
| testdb2 | latency = + 4.409 ms <br/> tps = - 619.163157   | latency = + 11.474 ms <br/> tps = - 727.248002  | latency = + 47.67 ms <br/> tps = - 1014.753687    |
| testdb3 | latency = + 4.151 ms <br/> tps = - 557.928314   | latency = + 10.948 ms <br/> tps = - 696.435983  | latency = + 68.808 ms <br/> tps = - 1218.470015   |
| testdb4 | latency = + 65.758 ms <br/> tps = - 1204.509189 | latency = + 64.042 ms <br/> tps = - 3416.081538 | latency = - 13.095 ms <br/> tps = + 1183.844992   |
| testdb5 | latency = + 35.968 ms <br/> tps = - 294.735532  | latency = + 57.782 ms <br/> tps = - 1801.039438 | latency = - 5873.179 ms <br/> tps = + 3055.178965 |
| testdb6 | latency = + 101.374 ms <br/> tps = - 782.550485 | latency = + 5.231 ms <br/> tps = - 4935.733057  | latency = - 0.021 ms <br/> tps = + 19.517665      |
| testdb7 | latency = + 31.452 ms <br/> tps = - 9013.215549 | latency = - 0.05 ms <br/> tps = + 162.700332    | latency = - 0.69 ms <br/> tps = + 367.139438      |



-M = extended

|         | c = 5                                            | c = 50                                          | c = 200                                          |
|---------|--------------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = + 7.85 ms <br/> tps = - 342.741924     | latency = + 78.556 ms <br/> tps = - 308.786133  | latency = + 182.087 ms <br/> tps = - 122.623482  |
| testdb2 | latency = + 4.273 ms <br/> tps = - 670.218961    | latency = + 19.713 ms <br/> tps = - 1387.061858 | latency = + 63.548 ms <br/> tps = - 1221.712098  |
| testdb3 | latency = + 3.727 ms <br/> tps = - 542.554027    | latency = + 16.239 ms <br/> tps = - 1016.261177 | latency = + 66.124 ms <br/> tps = - 1210.520334  |
| testdb4 | latency = + 62.013 ms <br/> tps = - 1121.970559  | latency = + 4.709 ms <br/> tps = - 641.855365   | latency = + 9.231 ms <br/> tps = - 715.320059    |
| testdb5 | latency = + 53.338 ms <br/> tps = - 338.592575   | latency = - 6.482 ms <br/> tps = + 457.155163   | latency = - 4070.57 ms <br/> tps = + 2138.170385 |
| testdb6 | latency = + 109.937 ms <br/> tps = - 6544.653216 | latency = + 0.337 ms <br/> tps = - 630.202299   | latency = + 12.801 ms <br/> tps = - 3737.382751  |
| testdb7 | latency = + 22.251 ms <br/> tps = - 7765.139567  | latency = - 0.132 ms <br/> tps = + 298.766336   | latency = - 0.829 ms <br/> tps = + 327.656887    |

Интересно, что при c=50 и c=200 таблицы с партициями, наоборот, дали выигрыш по скорости работы при работе с autovacuum. 


-f custom_select.sql

|         | c = 5                                            | c = 50                                         |
|---------|--------------------------------------------------|------------------------------------------------|
| testdb1 | latency = - 1.612 ms <br/> tps = + 2.362607      | latency = - 21.973 ms <br/> tps = + 4.012281   |
| testdb2 | latency = - 35.766 ms <br/> tps = + 0.572747     | latency = - 261.439 ms <br/> tps = + 0.523539  |
| testdb3 | latency = - 15.436 ms <br/> tps = + 0.196148     | latency = - 272.005 ms <br/> tps = + 0.249464  |
| testdb4 | latency = + 184302.336 ms <br/> tps = - 0.723115 | latency = - 32614.433 ms <br/> tps = + 0.37281 |
| testdb5 | latency = + 76750.701 ms <br/> tps = - 0.100882  | latency = - 3906.817 ms <br/> tps = + 0.072728 |
| testdb6 | latency = + 191877.829 ms <br/> tps = - 0.835399 | latency = - 227.929 ms <br/> tps = + 0.013988  |
| testdb7 | latency = + 46503.371 ms <br/> tps = - 0.726909  | latency = - 2219.921 ms <br/> tps = + 0.037224 |

Для третьего кейса значительно выросло latency на небольшом кол-ве клиентов и значительно упало на большом кол-ве клиентов.

В целом autovacuum замедлил работу почти каждой БД в 1.5-2 раза. 


### Эксперимент №8

Оставим изменения с эксперимента 7. 

Теперь отключим параметр `synchronous_commit`, чтобы сервер не сообщал об успешном выполнении операции. 
В файле `pgtune.conf` добавим строчку `synchronous_commit = off`.

Попробуем отключить ещё параметр `fsync` и `full_page_writes`. 
Первая настройка отключит прерывания на проверку записи данных на физический диск. 

В файл `postgres.conf` необходимо установить значения:
```
fsync = off
full_page_writes = off
```

Полный конфиг файла `pgtune.conf` и `postgresql.conf` можно посмотреть в [Конфигуарция для эксперимента №8](/exam/configs.md#конфигуарция-для-эксперимента-8)


В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                       | c = 50                                      | c = 200                                      |
|---------|---------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 0.722 ms <br/> tps = 6913.481329  | latency = 12.359 ms <br/> tps = 4043.113464 | latency = 103.572 ms <br/> tps = 1927.041663 |
| testdb2 | latency = 0.506 ms <br/> tps = 9848.331704  | latency = 4.395 ms <br/> tps = 11315.221526 | latency = 24.724 ms <br/> tps = 8064.765808  |
| testdb3 | latency = 0.551 ms <br/> tps = 9048.506803  | latency = 4.837 ms <br/> tps = 10285.725150 | latency = 26.774 ms <br/> tps = 7445.478423  |
| testdb4 | latency = 0.495 ms <br/> tps = 10052.534168 | latency = 3.554 ms <br/> tps = 13939.501143 | latency = 17.147 ms <br/> tps = 11549.896951 |
| testdb5 | latency = 0.544 ms <br/> tps = 9158.007690  | latency = 3.996 ms <br/> tps = 12408.543087 | latency = 19.499 ms <br/> tps = 10165.594215 |
| testdb6 | latency = 0.518 ms <br/> tps = 9610.580657  | latency = 3.498 ms <br/> tps = 14165.157676 | latency = 16.607 ms <br/> tps = 11926.391863 |
| testdb7 | latency = 0.778 ms <br/> tps = 6409.002730  | latency = 3.995 ms <br/> tps = 12409.541115 | latency = 18.754 ms <br/> tps = 10572.719376 |

</details>

<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 0.838 ms <br/> tps = 5956.839395 | latency = 13.572 ms <br/> tps = 3681.744545 | latency = 103.586 ms <br/> tps = 1926.755448 |
| testdb2 | latency = 0.583 ms <br/> tps = 8548.244721 | latency = 5.014 ms <br/> tps = 9923.423604  | latency = 27.844 ms <br/> tps = 7160.870515  |
| testdb3 | latency = 0.629 ms <br/> tps = 7922.989917 | latency = 5.609 ms <br/> tps = 8875.646283  | latency = 30.132 ms <br/> tps = 6617.891322  |
| testdb4 | latency = 0.570 ms <br/> tps = 8745.196250 | latency = 4.262 ms <br/> tps = 11634.817806 | latency = 20.404 ms <br/> tps = 9714.611317  |
| testdb5 | latency = 0.624 ms <br/> tps = 7989.299901 | latency = 4.817 ms <br/> tps = 10301.651317 | latency = 22.837 ms <br/> tps = 8678.856959  |
| testdb6 | latency = 0.577 ms <br/> tps = 8630.377645 | latency = 4.181 ms <br/> tps = 11861.727587 | latency = 19.973 ms <br/> tps = 9925.623743  |
| testdb7 | latency = 0.634 ms <br/> tps = 7860.510414 | latency = 4.639 ms <br/> tps = 10694.382748 | latency = 21.896 ms <br/> tps = 9056.830111  |

</details>

<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                      | c = 50                                      |
|---------|--------------------------------------------|---------------------------------------------|
| testdb1 | latency = 61.430 ms <br/> tps = 81.331523  | latency = 531.466 ms <br/> tps = 93.746754  |
| testdb2 | latency = 543.612 ms <br/> tps = 9.163616  | latency = 4863.614 ms <br/> tps = 10.113629 |
| testdb3 | latency = 612.413 ms <br/> tps = 8.107522  | latency = 5498.921 ms <br/> tps = 8.891683  |
| testdb4 | latency = 5279.318 ms <br/> tps = 0.929841 | latency = 49890.076 ms <br/> tps = 0.972685 |
| testdb5 | latency = 5585.326 ms <br/> tps = 0.863358 | latency = 53686.476 ms <br/> tps = 0.902025 |
| testdb6 | latency = 5346.303 ms <br/> tps = 0.903362 | latency = 50105.593 ms <br/> tps = 0.968406 |
| testdb7 | latency = 5796.775 ms <br/> tps = 0.830763 | latency = 54487.650 ms <br/> tps = 0.890032 |

</details>

Полный отчет тестов представлен в файле [experiment 8](/exam/experiments/e_8.md).


### Оценка времени между 7 и 8 экспериментами

-M = simple

|         | c = 5                                            | c = 50                                           | c = 200                                          |
|---------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 13.962 ms <br/> tps = + 6573.067998  | latency = - 123.641 ms <br/> tps = + 3676.550746 | latency = - 483.019 ms <br/> tps = + 1589.732508 |
| testdb2 | latency = - 8.056 ms <br/> tps = + 9264.663884   | latency = - 29.968 ms <br/> tps = + 9863.144028  | latency = - 98.955 ms <br/> tps = + 6455.734895  |
| testdb3 | latency = - 7.964 ms <br/> tps = + 8461.632352   | latency = - 29.168 ms <br/> tps = + 8817.322115  | latency = - 119.345 ms <br/> tps = + 6086.256304 |
| testdb4 | latency = - 69.176 ms <br/> tps = + 9980.786017  | latency = - 72.727 ms <br/> tps = + 13285.304288 | latency = - 23.633 ms <br/> tps = + 6671.721791  |
| testdb5 | latency = - 47.989 ms <br/> tps = + 9055.010979  | latency = - 74.172 ms <br/> tps = + 11769.984265 | latency = - 44.998 ms <br/> tps = + 7081.618552  |
| testdb6 | latency = - 106.885 ms <br/> tps = + 9564.102886 | latency = - 6.823 ms <br/> tps = + 9337.028349   | latency = - 2.286 ms <br/> tps = + 1434.672463   |
| testdb7 | latency = - 31.217 ms <br/> tps = + 6252.784875  | latency = + 0.106 ms <br/> tps = - 336.833487    | latency = - 0.277 ms <br/> tps = + 156.571365    |


-M = extended

|         | c = 5                                            | c = 50                                          | c = 200                                          |
|---------|--------------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 14.483 ms <br/> tps = + 5630.554556  | latency = - 145.13 ms <br/> tps = + 3367.484441 | latency = - 540.841 ms <br/> tps = + 1619.643315 |
| testdb2 | latency = - 7.587 ms <br/> tps = + 7936.655668   | latency = - 33.247 ms <br/> tps = + 8619.175318 | latency = - 110.776 ms <br/> tps = + 5726.740822 |
| testdb3 | latency = - 7.381 ms <br/> tps = + 7299.240502   | latency = - 31.889 ms <br/> tps = + 7544.122621 | latency = - 112.287 ms <br/> tps = + 5221.645542 |
| testdb4 | latency = - 65.613 ms <br/> tps = + 8669.722357  | latency = - 14.652 ms <br/> tps = + 8998.852216 | latency = - 34.982 ms <br/> tps = + 6121.097439  |
| testdb5 | latency = - 64.756 ms <br/> tps = + 7912.927301  | latency = - 18.73 ms <br/> tps = + 8182.881913  | latency = - 68.41 ms <br/> tps = + 6496.449246   |
| testdb6 | latency = - 110.117 ms <br/> tps = + 8585.243216 | latency = - 1.135 ms <br/> tps = + 2516.708442  | latency = - 13.195 ms <br/> tps = + 3930.807928  |
| testdb7 | latency = - 22.241 ms <br/> tps = + 7642.02835   | latency = + 0.036 ms <br/> tps = - 81.336764    | latency = - 0.245 ms <br/> tps = + 104.31966     |


-f custom_select.sql

|         | c = 5                                            | c = 50                                         |
|---------|--------------------------------------------------|------------------------------------------------|
| testdb1 | latency = + 3.435 ms <br/> tps = - 4.845052      | latency = + 8.772 ms <br/> tps = - 1.662545    |
| testdb2 | latency = + 4.606 ms <br/> tps = - 0.051479      | latency = + 140.505 ms <br/> tps = - 0.233114  |
| testdb3 | latency = + 20.117 ms <br/> tps = - 0.286007     | latency = + 244.41 ms <br/> tps = - 0.254366   |
| testdb4 | latency = - 185355.076 ms <br/> tps = + 0.903676 | latency = + 2991.352 ms <br/> tps = - 0.014993 |
| testdb5 | latency = - 103831.739 ms <br/> tps = + 0.818403 | latency = + 1992.876 ms <br/> tps = - 0.032787 |
| testdb6 | latency = - 192176.954 ms <br/> tps = + 0.878141 | latency = - 359.665 ms <br/> tps = - 0.000807  |
| testdb7 | latency = - 46517.727 ms <br/> tps = + 0.738586  | latency = + 1041.102 ms <br/> tps = - 0.020488 |

В этом кейсе только БД 6 (unlogged table) показала значительно улучшение результата. Остальные БД дали большое `latency`.


Вывод: в целом, ожидаемо, практически все БД дали большой прирост в скорости. Но БД 7 (s=100, partitions=20, unlogged table)
показала самый плохой результат, а в ряде тестов отрицательные значения для tps. Можно предположить, 
что при таких настройках и конфигурациях, таблицы этой БД упирались в свои лимиты по конфигурации или по физическим возможностям ВМ.



### Эксперимент №9

Главная отличительная особенность SSD диска от HDD в яндекс облаке:
Макс. IOPS 1000 / 1000 (у HDD 300/300)
Макс. bandwidth 15 / 15 МБ/с (у HDD 30/30)


Сделаем запуск тестов с начальными настройками по умолчанию.
В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                       | c = 50                                      | c = 200                              |
|---------|---------------------------------------------|---------------------------------------------|--------------------------------------|
| testdb1 | latency = 8.539 ms <br/> tps = 585.286624   | latency = 86.419 ms <br/> tps = 577.765975  | latency = error ms <br/> tps = error |
| testdb2 | latency = 6.347 ms <br/> tps = 787.271012   | latency = 26.585 ms <br/> tps = 1878.413376 | latency = error ms <br/> tps = error |
| testdb3 | latency = 6.486 ms <br/> tps = 770.204669   | latency = 27.203 ms <br/> tps = 1832.261390 | latency = error ms <br/> tps = error |
| testdb4 | latency = 11.532 ms <br/> tps = 433.240596  | latency = 167.718 ms <br/> tps = 297.891987 | latency = error ms <br/> tps = error |
| testdb5 | latency = 12.998 ms <br/> tps = 384.487688  | latency = 103.830 ms <br/> tps = 480.190815 | latency = error ms <br/> tps = error |
| testdb6 | latency = 0.460 ms <br/> tps = 10823.545745 | latency = 10.111 ms <br/> tps = 4932.895899 | latency = error ms <br/> tps = error |
| testdb7 | latency = 0.828 ms <br/> tps = 6026.530604  | latency = 7.039 ms <br/> tps = 6910.170854  | latency = error ms <br/> tps = error |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                              |
|---------|--------------------------------------------|---------------------------------------------|--------------------------------------|
| testdb1 | latency = 9.731 ms <br/> tps = 513.712751  | latency = 89.703 ms <br/> tps = 556.515589  | latency = error ms <br/> tps = error |
| testdb2 | latency = 5.929 ms <br/> tps = 842.649067  | latency = 32.584 ms <br/> tps = 1532.788599 | latency = error ms <br/> tps = error |
| testdb3 | latency = 6.294 ms <br/> tps = 793.790857  | latency = 31.295 ms <br/> tps = 1595.714002 | latency = error ms <br/> tps = error |
| testdb4 | latency = 16.236 ms <br/> tps = 307.830383 | latency = 115.710 ms <br/> tps = 430.986813 | latency = error ms <br/> tps = error |
| testdb5 | latency = 17.704 ms <br/> tps = 282.161966 | latency = 132.586 ms <br/> tps = 376.852144 | latency = error ms <br/> tps = error |
| testdb6 | latency = 1.010 ms <br/> tps = 4941.902877 | latency = 7.746 ms <br/> tps = 6209.131846  | latency = error ms <br/> tps = error |
| testdb7 | latency = 0.806 ms <br/> tps = 6187.594206 | latency = 5.802 ms <br/> tps = 8573.170738  | latency = error ms <br/> tps = error |
</details>

<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                      | c = 50                                      |
|---------|--------------------------------------------|---------------------------------------------|
| testdb1 | latency = 51.132 ms <br/> tps = 97.708971  | latency = 472.485 ms <br/> tps = 105.589073 |
| testdb2 | latency = 478.972 ms <br/> tps = 10.409222 | latency = 4428.042 ms <br/> tps = 11.061941 |
| testdb3 | latency = 549.878 ms <br/> tps = 9.055059  | latency = 4690.567 ms <br/> tps = 10.483994 |
| testdb4 | latency = 4683.383 ms <br/> tps = 1.032323 | latency = 46950.772 ms <br/> tps = 1.039258 |
| testdb5 | latency = 8135.170 ms <br/> tps = 0.601175 | latency = 48602.384 ms <br/> tps = 1.000995 |
| testdb6 | latency = 5005.891 ms <br/> tps = 0.982278 | latency = 51668.434 ms <br/> tps = 0.932692 |
| testdb7 | latency = 5264.385 ms <br/> tps = 0.930786 | latency = 50961.512 ms <br/> tps = 0.962671 |

</details>

Полный отчет тестов представлен в файле [experiment 9](/exam/experiments/e_9.md).


### Оценка времени между 1 и 9 экспериментами

-M = simple

|         | c = 5                                         | c = 50                                           | c = 200         |
|---------|-----------------------------------------------|--------------------------------------------------|-----------------|
| testdb1 | latency = + 0.721 ms <br/> tps = - 54.143152  | latency = + 7.473 ms <br/> tps = - 54.264709     | Can't calculate |
| testdb2 | latency = - 0.633 ms <br/> tps = + 71.337848  | latency = - 3.577 ms <br/> tps = + 222.938742    | Can't calculate |
| testdb3 | latency = + 0.983 ms <br/> tps = - 137.607098 | latency = - 3.688 ms <br/> tps = + 217.425869    | Can't calculate |
| testdb4 | latency = + 4.505 ms <br/> tps = - 277.765526 | latency = + 135.055 ms <br/> tps = - 1230.574688 | Can't calculate |
| testdb5 | latency = - 1.106 ms <br/> tps = + 30.57514   | latency = - 72.304 ms <br/> tps = + 199.060036   | Can't calculate |
| testdb6 | latency = - 0.102 ms <br/> tps = + 1951.77321 | latency = + 3.399 ms <br/> tps = - 2487.002921   | Can't calculate |
| testdb7 | latency = + 0.099 ms <br/> tps = - 815.58238  | latency = - 0.31 ms <br/> tps = + 134.729326     | Can't calculate |


-M = extended

|         | c = 5                                          | c = 50                                         | c = 200         |
|---------|------------------------------------------------|------------------------------------------------|-----------------|
| testdb1 | latency = + 2.174 ms <br/> tps = - 147.808278  | latency = + 11.528 ms <br/> tps = - 82.09651   | Can't calculate |
| testdb2 | latency = - 0.143 ms <br/> tps = + 19.733689   | latency = - 6.717 ms <br/> tps = + 263.071827  | Can't calculate |
| testdb3 | latency = + 0.437 ms <br/> tps = - 59.360911   | latency = - 7.186 ms <br/> tps = + 297.867038  | Can't calculate |
| testdb4 | latency = + 7.065 ms <br/> tps = - 237.061431  | latency = - 25.014 ms <br/> tps = + 84.235325  | Can't calculate |
| testdb5 | latency = - 3.937 ms <br/> tps = + 51.279145   | latency = - 10.043 ms <br/> tps = + 39.204005  | Can't calculate |
| testdb6 | latency = + 0.171 ms <br/> tps = - 1003.751817 | latency = + 0.359 ms <br/> tps = - 533.371973  | Can't calculate |
| testdb7 | latency = - 0.036 ms <br/> tps = + 263.997534  | latency = - 1.078 ms <br/> tps = + 1830.744078 | Can't calculate |


-f custom_select.sql

|         | c = 5                                          | c = 50                                         |
|---------|------------------------------------------------|------------------------------------------------|
| testdb1 | latency = - 7.811 ms <br/> tps = + 12.930412   | latency = - 59.941 ms <br/> tps = + 11.957537  |
| testdb2 | latency = - 73.736 ms <br/> tps = + 1.397488   | latency = - 883.873 ms <br/> tps = + 1.974258  |
| testdb3 | latency = - 67.908 ms <br/> tps = + 1.006269   | latency = - 657.54 ms <br/> tps = + 1.511937   |
| testdb4 | latency = - 664.305 ms <br/> tps = + 0.115181  | latency = - 5212.866 ms <br/> tps = + 0.109089 |
| testdb5 | latency = - 2098.502 ms <br/> tps = + 0.120461 | latency = - 4406.036 ms <br/> tps = + 0.093109 |
| testdb6 | latency = - 321.472 ms <br/> tps = + 0.074584  | latency = - 5099.704 ms <br/> tps = + 0.081633 |
| testdb7 | latency = - 459.612 ms <br/> tps = + 0.074181  | latency = - 2826.621 ms <br/> tps = + 0.078248 |


При стандартных настройках PostgreSQL выигрыша от SSD диска практически не наблюдается. Но хорошо видно, 
как в третьем тесте с кастомным SQL упало значение `latency`, т.е. время задержки значительно ниже, 
чем у HHD, но на работе самой БД это никак не отражено.


### Эксперимент №10

Эксперимент: улучшить конфигурацию кластера при помощи pgtune.

Задаим конфигурацию кластера в pgtune и сгенерируем конфиг для:
```
DB Version: 14
OS Type: linux
DB Type: oltp
Total Memory (RAM): 16 GB
CPUs num: 8
Connections num: 1000
Data Storage: ssd
```

Полный конфиг файла `pgtune.conf` можно посмотреть в [Конфигуарция для эксперимента №10](/exam/configs.md#конфигуарция-для-эксперимента-10)

Полученный конфиг для данной конфигурации запишем в файл `pgtune.conf`:
```shell
sudo touch /var/lib/pgsql/14/data/conf.d/pgtune.conf
sudo vi /var/lib/pgsql/14/data/conf.d/pgtune.conf
```


Сделаем рестарт, чтобы значения применились:
```shell
sudo systemctl stop postgresql-14
sudo systemctl start postgresql-14
```

В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                       | c = 50                                      | c = 200                                      |
|---------|---------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 7.426 ms <br/> tps = 673.174924   | latency = 81.037 ms <br/> tps = 616.231663  | latency = 415.302 ms <br/> tps = 478.322903  |
| testdb2 | latency = 5.612 ms <br/> tps = 890.272943   | latency = 19.992 ms <br/> tps = 2497.285686 | latency = 83.433 ms <br/> tps = 2389.385239  |
| testdb3 | latency = 5.058 ms <br/> tps = 987.639588   | latency = 23.512 ms <br/> tps = 2120.191318 | latency = 75.851 ms <br/> tps = 2628.330618  |
| testdb4 | latency = 7.017 ms <br/> tps = 711.803678   | latency = 79.619 ms <br/> tps = 627.408993  | latency = 192.996 ms <br/> tps = 1034.062349 |
| testdb5 | latency = 7.782 ms <br/> tps = 641.925591   | latency = 76.619 ms <br/> tps = 651.228151  | latency = 444.267 ms <br/> tps = 447.964800  |
| testdb6 | latency = 0.450 ms <br/> tps = 11069.395911 | latency = 3.203 ms <br/> tps = 15467.313774 | latency = 15.505 ms <br/> tps = 12773.557689 |
| testdb7 | latency = 0.497 ms <br/> tps = 10010.190360 | latency = 3.572 ms <br/> tps = 13879.246821 | latency = 17.057 ms <br/> tps = 11620.898729 |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 7.195 ms <br/> tps = 694.774441  | latency = 87.925 ms <br/> tps = 567.964069  | latency = 445.068 ms <br/> tps = 445.453677  |
| testdb2 | latency = 4.180 ms <br/> tps = 1194.983742 | latency = 18.873 ms <br/> tps = 2645.119917 | latency = 79.710 ms <br/> tps = 2502.128354  |
| testdb3 | latency = 4.858 ms <br/> tps = 1028.432271 | latency = 19.456 ms <br/> tps = 2566.179632 | latency = 77.250 ms <br/> tps = 2579.992450  |
| testdb4 | latency = 6.885 ms <br/> tps = 725.604592  | latency = 68.350 ms <br/> tps = 730.710084  | latency = 161.082 ms <br/> tps = 1237.422952 |
| testdb5 | latency = 11.033 ms <br/> tps = 452.930050 | latency = 99.533 ms <br/> tps = 501.528194  | latency = 313.986 ms <br/> tps = 634.597113  |
| testdb6 | latency = 0.528 ms <br/> tps = 9427.732751 | latency = 3.803 ms <br/> tps = 13037.205739 | latency = 18.294 ms <br/> tps = 10840.652851 |
| testdb7 | latency = 0.579 ms <br/> tps = 8608.782936 | latency = 4.225 ms <br/> tps = 11742.897465 | latency = 20.278 ms <br/> tps = 9778.372450  |

</details>

<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                      | c = 50                                      |
|---------|--------------------------------------------|---------------------------------------------|
| testdb1 | latency = 52.906 ms <br/> tps = 94.462956  | latency = 478.200 ms <br/> tps = 104.273656 |
| testdb2 | latency = 492.847 ms <br/> tps = 10.100708 | latency = 4432.163 ms <br/> tps = 10.953594 |
| testdb3 | latency = 532.303 ms <br/> tps = 9.361505  | latency = 4758.178 ms <br/> tps = 10.285670 |
| testdb4 | latency = 7565.611 ms <br/> tps = 0.630762 | latency = 45432.683 ms <br/> tps = 1.073787 |
| testdb5 | latency = 8275.276 ms <br/> tps = 0.590364 | latency = 49202.653 ms <br/> tps = 0.993721 |
| testdb6 | latency = 5031.273 ms <br/> tps = 0.973296 | latency = 47093.037 ms <br/> tps = 1.035838 |
| testdb7 | latency = 5397.320 ms <br/> tps = 0.895366 | latency = 51378.487 ms <br/> tps = 0.943040 |

</details>

Полный отчет тестов представлен в файле [experiment 10](/exam/experiments/e_10.md).


### Оценка времени между 2 и 10 экспериментами

-M = simple

|         | c = 5                                           | c = 50                                          | c = 200                                          |
|---------|-------------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 0.152 ms <br/> tps = + 13.533259    | latency = + 5.111 ms <br/> tps = - 41.330364    | latency = + 27.018 ms <br/> tps = - 33.718104    |
| testdb2 | latency = + 1.459 ms <br/> tps = - 312.558034   | latency = - 2.897 ms <br/> tps = + 317.960186   | latency = + 7.424 ms <br/> tps = - 234.399361    |
| testdb3 | latency = + 0.694 ms <br/> tps = - 157.163177   | latency = + 0.455 ms <br/> tps = - 44.6477      | latency = - 1.46 ms <br/> tps = + 50.638484      |
| testdb4 | latency = + 3.104 ms <br/> tps = - 564.453662   | latency = + 67.38 ms <br/> tps = - 3442.8694    | latency = + 139.121 ms <br/> tps = - 2660.267819 |
| testdb5 | latency = - 4.783 ms <br/> tps = + 244.193348   | latency = + 56.233 ms <br/> tps = - 1788.370109 | latency = - 5493.409 ms <br/> tps = + 419.168102 |
| testdb6 | latency = - 5.579 ms <br/> tps = + 10240.367655 | latency = - 1.887 ms <br/> tps = + 5703.45139   | latency = - 3.409 ms <br/> tps = + 2301.355954   |
| testdb7 | latency = - 0.046 ms <br/> tps = + 840.756956   | latency = - 0.367 ms <br/> tps = + 1295.572551  | latency = - 2.664 ms <br/> tps = + 1571.890156   |


-M = extended

|         | c = 5                                          | c = 50                                          | c = 200                                          |
|---------|------------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 0.276 ms <br/> tps = + 25.747678   | latency = + 7.779 ms <br/> tps = - 55.082168    | latency = - 17.272 ms <br/> tps = + 15.718062    |
| testdb2 | latency = + 0.283 ms <br/> tps = - 86.824272   | latency = + 0.325 ms <br/> tps = - 46.190227    | latency = + 4.638 ms <br/> tps = - 153.713437    |
| testdb3 | latency = + 0.575 ms <br/> tps = - 137.871171  | latency = - 1.803 ms <br/> tps = + 218.394793   | latency = + 0.955 ms <br/> tps = - 26.773664     |
| testdb4 | latency = + 2.715 ms <br/> tps = - 471.83986   | latency = + 54.145 ms <br/> tps = - 2547.110871 | latency = + 114.927 ms <br/> tps = - 3071.410985 |
| testdb5 | latency = - 1.009 ms <br/> tps = + 37.964875   | latency = + 69.504 ms <br/> tps = - 1160.086047 | latency = - 3847.831 ms <br/> tps = + 590.359785 |
| testdb6 | latency = - 0.229 ms <br/> tps = + 2837.945106 | latency = - 1.176 ms <br/> tps = + 3061.984295  | latency = - 2.073 ms <br/> tps = + 1108.454285   |
| testdb7 | latency = - 0.045 ms <br/> tps = + 625.161305  | latency = - 0.51 ms <br/> tps = + 1265.944289   | latency = - 2.692 ms <br/> tps = + 1153.518886   |


-f custom_select.sql

|         | c = 5                                           | c = 50                                          |
|---------|-------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = - 6.701 ms <br/> tps = + 10.648988    | latency = - 66.467 ms <br/> tps = + 12.876638   |
| testdb2 | latency = - 81.925 ms <br/> tps = + 1.45836     | latency = - 552.385 ms <br/> tps = + 1.13039    |
| testdb3 | latency = - 75.429 ms <br/> tps = + 1.164124    | latency = - 768.338 ms <br/> tps = + 1.389085   |
| testdb4 | latency = + 1233.553 ms <br/> tps = - 0.118518  | latency = - 34080.474 ms <br/> tps = + 0.458919 |
| testdb5 | latency = - 24391.088 ms <br/> tps = + 0.444527 | latency = - 6397.764 ms <br/> tps = + 0.131637  |
| testdb6 | latency = - 614.155 ms <br/> tps = + 0.112676   | latency = - 3600.15 ms <br/> tps = + 0.080613   |
| testdb7 | latency = - 413.811 ms <br/> tps = + 0.07628    | latency = - 4287.982 ms <br/> tps = + 0.069744  |


Вывод: на небольших БД (s=1, s=10) с небольшим кол-вом клиентов (c=5, c=50) прирост в скорости не сильно заметен, 
как на тех, у которых s=100 или c=200.
Лучше всего себя показывают БД 6 и 7 (с unlogged table).


### Эксперимент №11

Добавим настройки по autovacuum в `pgtune.conf`.

Полный конфиг файла `pgtune.conf` можно посмотреть в [Конфигуарция для эксперимента №11](/exam/configs.md#конфигуарция-для-эксперимента-11)

В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                       | c = 50                                      | c = 200                                      |
|---------|---------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 11.910 ms <br/> tps = 397.418203  | latency = 148.329 ms <br/> tps = 336.663074 | latency = 415.375 ms <br/> tps = 477.718043  |
| testdb2 | latency = 5.917 ms <br/> tps = 844.392831   | latency = 21.283 ms <br/> tps = 2345.596662 | latency = 76.545 ms <br/> tps = 2604.649771  |
| testdb3 | latency = 5.968 ms <br/> tps = 837.255908   | latency = 19.544 ms <br/> tps = 2554.406229 | latency = 78.564 ms <br/> tps = 2536.450227  |
| testdb4 | latency = 6.853 ms <br/> tps = 729.024471   | latency = 20.161 ms <br/> tps = 2473.626019 | latency = 31.373 ms <br/> tps = 6328.769255  |
| testdb5 | latency = 7.367 ms <br/> tps = 678.174906   | latency = 90.717 ms <br/> tps = 550.613337  | latency = 138.609 ms <br/> tps = 1438.811852 |
| testdb6 | latency = 0.461 ms <br/> tps = 10805.255125 | latency = 7.296 ms <br/> tps = 6826.813327  | latency = 15.405 ms <br/> tps = 12848.527820 |
| testdb7 | latency = 0.510 ms <br/> tps = 9768.635835  | latency = 3.650 ms <br/> tps = 13586.568730 | latency = 17.460 ms <br/> tps = 11357.782635 |

</details>

<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 2053.379 ms <br/> tps = 2.382074 | latency = 141.112 ms <br/> tps = 353.850419 | latency = 598.154 ms <br/> tps = 330.336622  |
| testdb2 | latency = 3.959 ms <br/> tps = 1261.738333 | latency = 18.407 ms <br/> tps = 2711.348141 | latency = 94.082 ms <br/> tps = 2119.047092  |
| testdb3 | latency = 5.274 ms <br/> tps = 947.311601  | latency = 18.362 ms <br/> tps = 2718.505957 | latency = 80.295 ms <br/> tps = 2482.725910  |
| testdb4 | latency = 6.209 ms <br/> tps = 804.497426  | latency = 14.418 ms <br/> tps = 3457.760081 | latency = 35.268 ms <br/> tps = 5638.009427  |
| testdb5 | latency = 10.267 ms <br/> tps = 486.717634 | latency = 75.296 ms <br/> tps = 663.415234  | latency = 115.495 ms <br/> tps = 1725.944895 |
| testdb6 | latency = 0.656 ms <br/> tps = 7603.992797 | latency = 4.212 ms <br/> tps = 11780.484910 | latency = 18.654 ms <br/> tps = 10629.599892 |
| testdb7 | latency = 0.603 ms <br/> tps = 8260.421765 | latency = 4.331 ms <br/> tps = 11455.702938 | latency = 20.416 ms <br/> tps = 9712.837556  |

</details>

<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                       | c = 50                                      |
|---------|---------------------------------------------|---------------------------------------------|
| testdb1 | latency = 52.821 ms <br/> tps = 94.609339   | latency = 482.082 ms <br/> tps = 103.461936 |
| testdb2 | latency = 482.955 ms <br/> tps = 10.306424  | latency = 4289.564 ms <br/> tps = 11.415964 |
| testdb3 | latency = 545.380 ms <br/> tps = 9.116103   | latency = 5022.807 ms <br/> tps = 9.735470  |
| testdb4 | latency = 34250.920 ms <br/> tps = 0.142808 | latency = 45557.370 ms <br/> tps = 1.074652 |
| testdb5 | latency = 67991.416 ms <br/> tps = 0.071464 | latency = 48469.454 ms <br/> tps = 1.000154 |
| testdb6 | latency = 4957.950 ms <br/> tps = 0.979911  | latency = 47022.728 ms <br/> tps = 1.029965 |
| testdb7 | latency = 5372.392 ms <br/> tps = 0.900473  | latency = 51574.250 ms <br/> tps = 0.943531 |

</details>

Полный отчет тестов представлен в файле [experiment 11](/exam/experiments/e_11.md).


### Оценка времени между 7 и 11 экспериментами

-M = simple

|         | c = 5                                             | c = 50                                          | c = 200                                         |
|---------|---------------------------------------------------|-------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = - 2.774 ms <br/> tps = + 57.004872      | latency = + 12.329 ms <br/> tps = - 29.899644   | latency = - 171.216 ms <br/> tps = + 140.408888 |
| testdb2 | latency = - 2.645 ms <br/> tps = + 260.725011     | latency = - 13.08 ms <br/> tps = + 893.519164   | latency = - 47.134 ms <br/> tps = + 995.618858  |
| testdb3 | latency = - 2.547 ms <br/> tps = + 250.381457     | latency = - 14.461 ms <br/> tps = + 1086.003194 | latency = - 67.555 ms <br/> tps = + 1177.228108 |
| testdb4 | latency = - 62.818 ms <br/> tps = + 657.27632     | latency = - 56.12 ms <br/> tps = + 1819.429164  | latency = - 9.407 ms <br/> tps = + 1450.594095  |
| testdb5 | latency = - 41.166 ms <br/> tps = + 575.178195    | latency = + 12.549 ms <br/> tps = - 87.945485   | latency = + 74.112 ms <br/> tps = - 1645.163811 |
| testdb6 | latency = - 106.942 ms <br/> tps = + 10758.777354 | latency = - 3.025 ms <br/> tps = + 1998.684     | latency = - 3.488 ms <br/> tps = + 2356.80842   |
| testdb7 | latency = - 31.485 ms <br/> tps = + 9612.41798    | latency = - 0.239 ms <br/> tps = + 840.194128   | latency = - 1.571 ms <br/> tps = + 941.634624   |


-M = extended

|         | c = 5                                            | c = 50                                          | c = 200                                         |
|---------|--------------------------------------------------|-------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = + 2038.058 ms <br/> tps = - 323.902765 | latency = - 17.59 ms <br/> tps = + 39.590315    | latency = - 46.273 ms <br/> tps = + 23.224489   |
| testdb2 | latency = - 4.211 ms <br/> tps = + 650.14928     | latency = - 19.854 ms <br/> tps = + 1407.099855 | latency = - 44.538 ms <br/> tps = + 684.917399  |
| testdb3 | latency = - 2.736 ms <br/> tps = + 323.562186    | latency = - 19.136 ms <br/> tps = + 1386.982295 | latency = - 62.124 ms <br/> tps = + 1086.48013  |
| testdb4 | latency = - 59.974 ms <br/> tps = + 729.023533   | latency = - 4.496 ms <br/> tps = + 821.794491   | latency = - 20.118 ms <br/> tps = + 2044.495549 |
| testdb5 | latency = - 55.113 ms <br/> tps = + 410.345034   | latency = + 51.749 ms <br/> tps = - 1455.35417  | latency = + 24.248 ms <br/> tps = - 456.462818  |
| testdb6 | latency = - 110.038 ms <br/> tps = + 7558.858368 | latency = - 1.104 ms <br/> tps = + 2435.465765  | latency = - 14.514 ms <br/> tps = + 4634.784077 |
| testdb7 | latency = - 22.272 ms <br/> tps = + 8041.939701  | latency = - 0.272 ms <br/> tps = + 679.983426   | latency = - 1.725 ms <br/> tps = + 760.327105   |


-f custom_select.sql

|         | c = 5                                            | c = 50                                         |
|---------|--------------------------------------------------|------------------------------------------------|
| testdb1 | latency = - 5.174 ms <br/> tps = + 8.432764      | latency = - 40.612 ms <br/> tps = + 8.052637   |
| testdb2 | latency = - 56.051 ms <br/> tps = + 1.091329     | latency = - 433.545 ms <br/> tps = + 1.069221  |
| testdb3 | latency = - 46.916 ms <br/> tps = + 0.722574     | latency = - 231.704 ms <br/> tps = + 0.589421  |
| testdb4 | latency = - 156383.474 ms <br/> tps = + 0.116643 | latency = - 1341.354 ms <br/> tps = + 0.086974 |
| testdb5 | latency = - 41425.649 ms <br/> tps = + 0.026509  | latency = - 3224.146 ms <br/> tps = + 0.065342 |
| testdb6 | latency = - 192565.307 ms <br/> tps = + 0.95469  | latency = - 3442.53 ms <br/> tps = + 0.060752  |
| testdb7 | latency = - 46942.11 ms <br/> tps = + 0.808296   | latency = - 1872.298 ms <br/> tps = + 0.033011 |


Самый большой прирост по скорости дала БД 6 (unlogged tables). 
У БД 7 (partitions=20, unlogged tables), выглядит, что тоже был выигрыш, но только на небольшом кол-ве клиентов. 
Как только кол-во клиентов было больше, работа в такой БД значительно занижалась.

Можно выдвинуть гипотезу, что все три БД с партициями (БД 3, 5, 7) дали плохой результат.


### Эксперимент №12

Эксперимент: изменим значения для autovacom, изменив `coasts` и `delay` для SSD диска.

Полный конфиг файла `pgtune.conf` и `postgresql.conf` можно посмотреть в [Конфигуарция для эксперимента №12](/exam/configs.md#конфигуарция-для-эксперимента-12)


В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 7.952 ms <br/> tps = 628.619445  | latency = 81.985 ms <br/> tps = 608.935506  | latency = 386.691 ms <br/> tps = 514.201105  |
| testdb2 | latency = 12.203 ms <br/> tps = 409.616544 | latency = 23.034 ms <br/> tps = 2167.881157 | latency = 78.288 ms <br/> tps = 2547.257229  |
| testdb3 | latency = 12.994 ms <br/> tps = 384.657528 | latency = 20.077 ms <br/> tps = 2486.477594 | latency = 82.636 ms <br/> tps = 2407.263669  |
| testdb4 | latency = 27.777 ms <br/> tps = 179.965051 | latency = 8.324 ms <br/> tps = 5979.620198  | latency = 163.757 ms <br/> tps = 1217.816591 |
| testdb5 | latency = 41.074 ms <br/> tps = 121.715664 | latency = 63.133 ms <br/> tps = 790.767309  | latency = 107.184 ms <br/> tps = 1856.020593 |
| testdb6 | latency = 33.766 ms <br/> tps = 148.052015 | latency = 5.415 ms <br/> tps = 9183.803820  | latency = 16.261 ms <br/> tps = 12177.099273 |
| testdb7 | latency = 20.465 ms <br/> tps = 244.291930 | latency = 3.915 ms <br/> tps = 12667.062450 | latency = 18.870 ms <br/> tps = 10507.970058 |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 8.761 ms <br/> tps = 570.570147  | latency = 80.836 ms <br/> tps = 617.650171  | latency = 409.938 ms <br/> tps = 484.643001  |
| testdb2 | latency = 4.232 ms <br/> tps = 1179.906367 | latency = 19.535 ms <br/> tps = 2554.818481 | latency = 95.711 ms <br/> tps = 2074.521829  |
| testdb3 | latency = 4.942 ms <br/> tps = 1010.911510 | latency = 22.660 ms <br/> tps = 2203.181289 | latency = 79.154 ms <br/> tps = 2517.196546  |
| testdb4 | latency = 24.137 ms <br/> tps = 207.081446 | latency = 7.787 ms <br/> tps = 6390.171685  | latency = 132.160 ms <br/> tps = 1508.785373 |
| testdb5 | latency = 45.517 ms <br/> tps = 109.831682 | latency = 37.218 ms <br/> tps = 1341.171644 | latency = 79.657 ms <br/> tps = 2500.949080  |
| testdb6 | latency = 18.003 ms <br/> tps = 277.675725 | latency = 4.798 ms <br/> tps = 10351.658025 | latency = 19.455 ms <br/> tps = 10195.406925 |
| testdb7 | latency = 15.301 ms <br/> tps = 326.742297 | latency = 4.609 ms <br/> tps = 10764.943212 | latency = 21.956 ms <br/> tps = 9033.465351  |

</details>


<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                        | c = 50                                      |
|---------|----------------------------------------------|---------------------------------------------|
| testdb1 | latency = 55.898 ms <br/> tps = 89.416434    | latency = 513.243 ms <br/> tps = 97.177946  |
| testdb2 | latency = 507.375 ms <br/> tps = 9.819470    | latency = 4522.940 ms <br/> tps = 10.771231 |
| testdb3 | latency = 595.797 ms <br/> tps = 8.339674    | latency = 5242.634 ms <br/> tps = 9.177851  |
| testdb4 | latency = 172227.731 ms <br/> tps = 0.028939 | latency = 48052.037 ms <br/> tps = 1.019210 |
| testdb5 | latency = 177292.829 ms <br/> tps = 0.027910 | latency = 51350.060 ms <br/> tps = 0.935483 |
| testdb6 | latency = 245130.542 ms <br/> tps = 0.020344 | latency = 48533.590 ms <br/> tps = 0.999264 |
| testdb7 | latency = 74408.050 ms <br/> tps = 0.065419  | latency = 52918.915 ms <br/> tps = 0.911722 |

</details>

Полный отчет тестов представлен в файле [experiment 12](/exam/experiments/e_12.md).


### Оценка времени между 11 и 12 экспериментами

-M = simple


|         | c = 5                                           | c = 50                                          | c = 200                                          |
|---------|-------------------------------------------------|-------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = - 3.958 ms <br/> tps = + 231.201242   | latency = - 66.344 ms <br/> tps = + 272.272432  | latency = - 28.684 ms <br/> tps = + 36.483062    |
| testdb2 | latency = + 6.286 ms <br/> tps = - 434.776287   | latency = + 1.751 ms <br/> tps = - 177.715505   | latency = + 1.743 ms <br/> tps = - 57.392542     |
| testdb3 | latency = + 7.026 ms <br/> tps = - 452.59838    | latency = + 0.533 ms <br/> tps = - 67.928635    | latency = + 4.072 ms <br/> tps = - 129.186558    |
| testdb4 | latency = + 20.924 ms <br/> tps = - 549.05942   | latency = - 11.837 ms <br/> tps = + 3505.994179 | latency = + 132.384 ms <br/> tps = - 5110.952664 |
| testdb5 | latency = + 33.707 ms <br/> tps = - 556.459242  | latency = - 27.584 ms <br/> tps = + 240.153972  | latency = - 31.425 ms <br/> tps = + 417.208741   |
| testdb6 | latency = + 33.305 ms <br/> tps = - 10657.20311 | latency = - 1.881 ms <br/> tps = + 2356.990493  | latency = + 0.856 ms <br/> tps = - 671.428547    |
| testdb7 | latency = + 19.955 ms <br/> tps = - 9524.343905 | latency = + 0.265 ms <br/> tps = - 919.50628    | latency = + 1.41 ms <br/> tps = - 849.812577     |


-M = extended

|         | c = 5                                            | c = 50                                         | c = 200                                         |
|---------|--------------------------------------------------|------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = - 2044.618 ms <br/> tps = + 568.188073 | latency = - 60.276 ms <br/> tps = + 263.799752 | latency = - 188.216 ms <br/> tps = + 154.306379 |
| testdb2 | latency = + 0.273 ms <br/> tps = - 81.831966     | latency = + 1.128 ms <br/> tps = - 156.52966   | latency = + 1.629 ms <br/> tps = - 44.525263    |
| testdb3 | latency = - 0.332 ms <br/> tps = + 63.599909     | latency = + 4.298 ms <br/> tps = - 515.324668  | latency = - 1.141 ms <br/> tps = + 34.470636    |
| testdb4 | latency = + 17.928 ms <br/> tps = - 597.41598    | latency = - 6.631 ms <br/> tps = + 2932.411604 | latency = + 96.892 ms <br/> tps = - 4129.224054 |
| testdb5 | latency = + 35.25 ms <br/> tps = - 376.885952    | latency = - 38.078 ms <br/> tps = + 677.75641  | latency = - 35.838 ms <br/> tps = + 775.004185  |
| testdb6 | latency = + 17.347 ms <br/> tps = - 7326.317072  | latency = + 0.586 ms <br/> tps = - 1428.826885 | latency = + 0.801 ms <br/> tps = - 434.192967   |
| testdb7 | latency = + 14.698 ms <br/> tps = - 7933.679468  | latency = + 0.278 ms <br/> tps = - 690.759726  | latency = + 1.54 ms <br/> tps = - 679.372205    |


-f custom_select.sql

|         | c = 5                                            | c = 50                                         |
|---------|--------------------------------------------------|------------------------------------------------|
| testdb1 | latency = + 3.077 ms <br/> tps = - 5.192905      | latency = + 31.161 ms <br/> tps = - 6.28399    |
| testdb2 | latency = + 24.42 ms <br/> tps = - 0.486954      | latency = + 233.376 ms <br/> tps = - 0.644733  |
| testdb3 | latency = + 50.417 ms <br/> tps = - 0.776429     | latency = + 219.827 ms <br/> tps = - 0.557619  |
| testdb4 | latency = + 137976.811 ms <br/> tps = - 0.113869 | latency = + 2494.667 ms <br/> tps = - 0.055442 |
| testdb5 | latency = + 109301.413 ms <br/> tps = - 0.043554 | latency = + 2880.606 ms <br/> tps = - 0.064671 |
| testdb6 | latency = + 240172.592 ms <br/> tps = - 0.959567 | latency = + 1510.862 ms <br/> tps = - 0.030701 |
| testdb7 | latency = + 69035.658 ms <br/> tps = - 0.835054  | latency = + 1344.665 ms <br/> tps = - 0.031809 |

В рамках эксперимент настроек между autovacuum для HDD и SSD для ВМ с SSD диском, можно сделать несколько выводов:
1. Либо яндекс облако в момент проведения теста занизило мощность ВМ с SSD, 
либо даже высокая скорость I/O (относительно ВМ с HDD у ВМ с SSD диском скорость больше в 3 раза), показатели стали хуже, 
этого недостаточно для частого и быстрого vacuum. 
2. БД с партициями (3, 5, 7) показали результаты лучше, чем другие БД.


### Эксперимент №13

Теперь отключим параметр `synchronous_commit`, чтобы сервер не сообщал об успешном выполнении операции. 
В файле `pgtune.conf` добавим строчку `synchronous_commit = off`.

Попробуем отключить ещё параметр `fsync` и `full_page_writes`. 
Первая настройка отключит прерывания на проверку записи данных на физический диск. 

В файл `postgres.conf` необходимо установить значения:
```
fsync = off
full_page_writes = off
```

Полный конфиг файла `pgtune.conf` и `postgresql.conf` можно посмотреть в [Конфигуарция для эксперимента №13](/exam/configs.md#конфигуарция-для-эксперимента-13)


В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                       | c = 50                                      | c = 200                                      |
|---------|---------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 0.719 ms <br/> tps = 6939.872850  | latency = 11.793 ms <br/> tps = 4236.578845 | latency = 91.407 ms <br/> tps = 2182.882076  |
| testdb2 | latency = 0.493 ms <br/> tps = 10110.200623 | latency = 4.271 ms <br/> tps = 11642.372937 | latency = 23.970 ms <br/> tps = 8318.965863  |
| testdb3 | latency = 0.542 ms <br/> tps = 9191.005232  | latency = 4.727 ms <br/> tps = 10525.555648 | latency = 26.322 ms <br/> tps = 7574.253748  |
| testdb4 | latency = 0.482 ms <br/> tps = 10316.397827 | latency = 3.482 ms <br/> tps = 14227.972158 | latency = 16.430 ms <br/> tps = 12053.006292 |
| testdb5 | latency = 0.534 ms <br/> tps = 9331.887954  | latency = 5.184 ms <br/> tps = 9583.102381  | latency = 18.750 ms <br/> tps = 10573.120985 |
| testdb6 | latency = 0.553 ms <br/> tps = 9012.253328  | latency = 3.473 ms <br/> tps = 14268.551546 | latency = 16.060 ms <br/> tps = 12327.365414 |
| testdb7 | latency = 0.535 ms <br/> tps = 9301.316518  | latency = 3.844 ms <br/> tps = 12896.381074 | latency = 18.286 ms <br/> tps = 10837.557973 |

</details>

<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 0.823 ms <br/> tps = 6068.548546 | latency = 13.124 ms <br/> tps = 3807.438325 | latency = 95.428 ms <br/> tps = 2091.657818  |
| testdb2 | latency = 0.572 ms <br/> tps = 8713.760401 | latency = 4.962 ms <br/> tps = 10029.595040 | latency = 27.077 ms <br/> tps = 7364.789115  |
| testdb3 | latency = 0.623 ms <br/> tps = 8004.542875 | latency = 5.426 ms <br/> tps = 9174.282857  | latency = 29.686 ms <br/> tps = 6718.477250  |
| testdb4 | latency = 0.563 ms <br/> tps = 8853.506795 | latency = 4.116 ms <br/> tps = 12048.717596 | latency = 19.592 ms <br/> tps = 10117.475641 |
| testdb5 | latency = 0.612 ms <br/> tps = 8143.207741 | latency = 4.630 ms <br/> tps = 10715.892502 | latency = 22.662 ms <br/> tps = 8749.241719  |
| testdb6 | latency = 0.560 ms <br/> tps = 8899.378441 | latency = 4.174 ms <br/> tps = 11882.919665 | latency = 19.840 ms <br/> tps = 9996.777649  |
| testdb7 | latency = 0.611 ms <br/> tps = 8156.708015 | latency = 4.598 ms <br/> tps = 10790.829555 | latency = 21.288 ms <br/> tps = 9313.541606  |

</details>


<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                      | c = 50                                      |
|---------|--------------------------------------------|---------------------------------------------|
| testdb1 | latency = 59.662 ms <br/> tps = 83.728242  | latency = 510.983 ms <br/> tps = 97.517985  |
| testdb2 | latency = 529.268 ms <br/> tps = 9.423943  | latency = 4778.585 ms <br/> tps = 10.243424 |
| testdb3 | latency = 584.965 ms <br/> tps = 8.500562  | latency = 5080.865 ms <br/> tps = 9.647574  |
| testdb4 | latency = 5124.000 ms <br/> tps = 0.948473 | latency = 49077.122 ms <br/> tps = 0.990281 |
| testdb5 | latency = 5643.921 ms <br/> tps = 0.844293 | latency = 53447.623 ms <br/> tps = 0.904629 |
| testdb6 | latency = 5258.045 ms <br/> tps = 0.925205 | latency = 49627.258 ms <br/> tps = 0.980850 |
| testdb7 | latency = 5670.903 ms <br/> tps = 0.848048 | latency = 54329.547 ms <br/> tps = 0.894297 |

</details>


Полный отчет тестов представлен в файле [experiment 13](/exam/experiments/e_13.md).



### Оценка времени между 8 и 13 экспериментами

-M = simple

|         | c = 5                                          | c = 50                                         | c = 200                                        |
|---------|------------------------------------------------|------------------------------------------------|------------------------------------------------|
| testdb1 | latency = - 0.003 ms <br/> tps = + 26.391521   | latency = - 0.566 ms <br/> tps = + 193.465381  | latency = - 12.165 ms <br/> tps = + 255.840413 |
| testdb2 | latency = - 0.013 ms <br/> tps = + 261.868919  | latency = - 0.124 ms <br/> tps = + 327.151411  | latency = - 0.754 ms <br/> tps = + 254.200055  |
| testdb3 | latency = - 0.009 ms <br/> tps = + 142.498429  | latency = - 0.11 ms <br/> tps = + 239.830498   | latency = - 0.452 ms <br/> tps = + 128.775325  |
| testdb4 | latency = - 0.013 ms <br/> tps = + 263.863659  | latency = - 0.072 ms <br/> tps = + 288.471015  | latency = - 0.717 ms <br/> tps = + 503.109341  |
| testdb5 | latency = - 0.01 ms <br/> tps = + 173.880264   | latency = + 1.188 ms <br/> tps = - 2825.440706 | latency = - 0.749 ms <br/> tps = + 407.52677   |
| testdb6 | latency = + 0.035 ms <br/> tps = - 598.327329  | latency = - 0.025 ms <br/> tps = + 103.39387   | latency = - 0.547 ms <br/> tps = + 400.973551  |
| testdb7 | latency = - 0.243 ms <br/> tps = + 2892.313788 | latency = - 0.151 ms <br/> tps = + 486.839959  | latency = - 0.468 ms <br/> tps = + 264.838597  |


-M = extended

|         | c = 5                                         | c = 50                                        | c = 200                                       |
|---------|-----------------------------------------------|-----------------------------------------------|-----------------------------------------------|
| testdb1 | latency = - 0.015 ms <br/> tps = + 111.709151 | latency = - 0.448 ms <br/> tps = + 125.69378  | latency = - 8.158 ms <br/> tps = + 164.90237  |
| testdb2 | latency = - 0.011 ms <br/> tps = + 165.51568  | latency = - 0.052 ms <br/> tps = + 106.171436 | latency = - 0.767 ms <br/> tps = + 203.9186   |
| testdb3 | latency = - 0.006 ms <br/> tps = + 81.552958  | latency = - 0.183 ms <br/> tps = + 298.636574 | latency = - 0.446 ms <br/> tps = + 100.585928 |
| testdb4 | latency = - 0.007 ms <br/> tps = + 108.310545 | latency = - 0.146 ms <br/> tps = + 413.89979  | latency = - 0.812 ms <br/> tps = + 402.864324 |
| testdb5 | latency = - 0.012 ms <br/> tps = + 153.90784  | latency = - 0.187 ms <br/> tps = + 414.241185 | latency = - 0.175 ms <br/> tps = + 70.38476   |
| testdb6 | latency = - 0.017 ms <br/> tps = + 269.000796 | latency = - 0.007 ms <br/> tps = + 21.192078  | latency = - 0.133 ms <br/> tps = + 71.153906  |
| testdb7 | latency = - 0.023 ms <br/> tps = + 296.197601 | latency = - 0.041 ms <br/> tps = + 96.446807  | latency = - 0.608 ms <br/> tps = + 256.711495 |


-f custom_select.sql

|         | c = 5                                         | c = 50                                        |
|---------|-----------------------------------------------|-----------------------------------------------|
| testdb1 | latency = - 1.768 ms <br/> tps = + 2.396719   | latency = - 20.483 ms <br/> tps = + 3.771231  |
| testdb2 | latency = - 14.344 ms <br/> tps = + 0.260327  | latency = - 85.029 ms <br/> tps = + 0.129795  |
| testdb3 | latency = - 27.448 ms <br/> tps = + 0.39304   | latency = - 418.056 ms <br/> tps = + 0.755891 |
| testdb4 | latency = - 155.318 ms <br/> tps = + 0.018632 | latency = - 812.954 ms <br/> tps = + 0.017596 |
| testdb5 | latency = + 58.595 ms <br/> tps = - 0.019065  | latency = - 238.853 ms <br/> tps = + 0.002604 |
| testdb6 | latency = - 88.258 ms <br/> tps = + 0.021843  | latency = - 478.335 ms <br/> tps = + 0.012444 |
| testdb7 | latency = - 125.872 ms <br/> tps = + 0.017285 | latency = - 158.103 ms <br/> tps = + 0.004265 |





### Оценка времени между 9 и 13 экспериментами


-M = simple

|         | c = 5                                           | c = 50                                            | c = 200         |
|---------|-------------------------------------------------|---------------------------------------------------|-----------------|
| testdb1 | latency = - 7.82 ms <br/> tps = + 6354.586226   | latency = - 74.626 ms <br/> tps = + 3658.81287    | Can't calculate |
| testdb2 | latency = - 5.854 ms <br/> tps = + 9322.929611  | latency = - 22.314 ms <br/> tps = + 9763.959561   | Can't calculate |
| testdb3 | latency = - 5.944 ms <br/> tps = + 8420.800563  | latency = - 22.476 ms <br/> tps = + 8693.294258   | Can't calculate |
| testdb4 | latency = - 11.05 ms <br/> tps = + 9883.157231  | latency = - 164.236 ms <br/> tps = + 13930.080171 | Can't calculate |
| testdb5 | latency = - 12.464 ms <br/> tps = + 8947.400266 | latency = - 98.646 ms <br/> tps = + 9102.911566   | Can't calculate |
| testdb6 | latency = + 0.093 ms <br/> tps = - 1811.292417  | latency = - 6.638 ms <br/> tps = + 9335.655647    | Can't calculate |
| testdb7 | latency = - 0.293 ms <br/> tps = + 3274.785914  | latency = - 3.195 ms <br/> tps = + 5986.21022     | Can't calculate |


-M = extended

|         | c = 5                                           | c = 50                                            | c = 200         |
|---------|-------------------------------------------------|---------------------------------------------------|-----------------|
| testdb1 | latency = - 8.908 ms <br/> tps = + 5554.835795  | latency = - 76.579 ms <br/> tps = + 3250.922736   | Can't calculate |
| testdb2 | latency = - 5.357 ms <br/> tps = + 7871.111334  | latency = - 27.622 ms <br/> tps = + 8496.806441   | Can't calculate |
| testdb3 | latency = - 5.671 ms <br/> tps = + 7210.752018  | latency = - 25.869 ms <br/> tps = + 7578.568855   | Can't calculate |
| testdb4 | latency = - 15.673 ms <br/> tps = + 8545.676412 | latency = - 111.594 ms <br/> tps = + 11617.730783 | Can't calculate |
| testdb5 | latency = - 17.092 ms <br/> tps = + 7861.045775 | latency = - 127.956 ms <br/> tps = + 10339.040358 | Can't calculate |
| testdb6 | latency = - 0.45 ms <br/> tps = + 3957.475564   | latency = - 3.572 ms <br/> tps = + 5673.787819    | Can't calculate |
| testdb7 | latency = - 0.195 ms <br/> tps = + 1969.113809  | latency = - 1.204 ms <br/> tps = + 2217.658817    | Can't calculate |


-f custom_select.sql

|         | c = 5                                          | c = 50                                         |
|---------|------------------------------------------------|------------------------------------------------|
| testdb1 | latency = + 8.53 ms <br/> tps = - 13.980729    | latency = + 38.498 ms <br/> tps = - 8.071088   |
| testdb2 | latency = + 50.296 ms <br/> tps = - 0.985279   | latency = + 350.543 ms <br/> tps = - 0.818517  |
| testdb3 | latency = + 35.087 ms <br/> tps = - 0.554497   | latency = + 390.298 ms <br/> tps = - 0.83642   |
| testdb4 | latency = + 440.617 ms <br/> tps = - 0.08385   | latency = + 2126.35 ms <br/> tps = - 0.048977  |
| testdb5 | latency = - 2491.249 ms <br/> tps = + 0.243118 | latency = + 4845.239 ms <br/> tps = - 0.096366 |
| testdb6 | latency = + 252.154 ms <br/> tps = - 0.057073  | latency = - 2041.176 ms <br/> tps = + 0.048158 |
| testdb7 | latency = + 406.518 ms <br/> tps = - 0.082738  | latency = + 3368.035 ms <br/> tps = - 0.068374 |






### Оценка времени между 1 и 13 экспериментами



-M = simple

|         | c = 5                                          | c = 50                                           | c = 200         |
|---------|------------------------------------------------|--------------------------------------------------|-----------------|
| testdb1 | latency = - 7.099 ms <br/> tps = + 6300.443074 | latency = - 67.153 ms <br/> tps = + 3604.548161  | Can't calculate |
| testdb2 | latency = - 6.487 ms <br/> tps = + 9394.267459 | latency = - 25.891 ms <br/> tps = + 9986.898303  | Can't calculate |
| testdb3 | latency = - 4.961 ms <br/> tps = + 8283.193465 | latency = - 26.164 ms <br/> tps = + 8910.720127  | Can't calculate |
| testdb4 | latency = - 6.545 ms <br/> tps = + 9605.391705 | latency = - 29.181 ms <br/> tps = + 12699.505483 | Can't calculate |
| testdb5 | latency = - 13.57 ms <br/> tps = + 8977.975406 | latency = - 170.95 ms <br/> tps = + 9301.971602  | Can't calculate |
| testdb6 | latency = - 0.009 ms <br/> tps = + 140.480793  | latency = - 3.239 ms <br/> tps = + 6848.652726   | Can't calculate |
| testdb7 | latency = - 0.194 ms <br/> tps = + 2459.203534 | latency = - 3.505 ms <br/> tps = + 6120.939546   | Can't calculate |


-M = extended

|         | c = 5                                          | c = 50                                            | c = 200         |
|---------|------------------------------------------------|---------------------------------------------------|-----------------|
| testdb1 | latency = - 6.734 ms <br/> tps = + 5407.027517 | latency = - 65.051 ms <br/> tps = + 3168.826226   | Can't calculate |
| testdb2 | latency = - 5.5 ms <br/> tps = + 7890.845023   | latency = - 34.339 ms <br/> tps = + 8759.878268   | Can't calculate |
| testdb3 | latency = - 5.234 ms <br/> tps = + 7151.391107 | latency = - 33.055 ms <br/> tps = + 7876.435893   | Can't calculate |
| testdb4 | latency = - 8.608 ms <br/> tps = + 8308.614981 | latency = - 136.608 ms <br/> tps = + 11701.966108 | Can't calculate |
| testdb5 | latency = - 21.029 ms <br/> tps = + 7912.32492 | latency = - 137.999 ms <br/> tps = + 10378.244363 | Can't calculate |
| testdb6 | latency = - 0.279 ms <br/> tps = + 2953.723747 | latency = - 3.213 ms <br/> tps = + 5140.415846    | Can't calculate |
| testdb7 | latency = - 0.231 ms <br/> tps = + 2233.111343 | latency = - 2.282 ms <br/> tps = + 4048.402895    | Can't calculate |


-f custom_select.sql

|         | c = 5                                          | c = 50                                         |
|---------|------------------------------------------------|------------------------------------------------|
| testdb1 | latency = + 0.719 ms <br/> tps = - 1.050317    | latency = - 21.443 ms <br/> tps = + 3.886449   |
| testdb2 | latency = - 23.44 ms <br/> tps = + 0.412209    | latency = - 533.33 ms <br/> tps = + 1.155741   |
| testdb3 | latency = - 32.821 ms <br/> tps = + 0.451772   | latency = - 267.242 ms <br/> tps = + 0.675517  |
| testdb4 | latency = - 223.688 ms <br/> tps = + 0.031331  | latency = - 3086.516 ms <br/> tps = + 0.060112 |
| testdb5 | latency = - 4589.751 ms <br/> tps = + 0.363579 | latency = + 439.203 ms <br/> tps = - 0.003257  |
| testdb6 | latency = - 69.318 ms <br/> tps = + 0.017511   | latency = - 7140.88 ms <br/> tps = + 0.129791  |
| testdb7 | latency = - 53.094 ms <br/> tps = - 0.008557   | latency = + 541.414 ms <br/> tps = + 0.009874  |





### Эксперимент №14

В этом эксперименте вернёмся к настройкам эксперимента №2 для ВМ с HDD диском, уберём изменения по `synchronous_commit = off`, 
`fsync` и `full_page_writes` в `postgresql.conf` и отключим некоторые настройки для построения плана запроса. 

Поключим следующие настройки:
```
enable_sort = off    
enable_seqscan = off
enable_partition_pruning = off
enable_parallel_append = off
enable_parallel_hash = off
enable_nestloop = off
enable_bitmapscan = off
```

Полный конфиг файла `pgtune.conf` можно посмотреть в [Конфигуарция для эксперимента №14](/exam/configs.md#конфигуарция-для-эксперимента-14)

В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 49.866 ms <br/> tps = 100.062228 | latency = 1884.970 ms <br/> tps = 24.472685 | latency = 6352.907 ms <br/> tps = 28.779339  |
| testdb2 | latency = 5.557 ms <br/> tps = 899.195348  | latency = 19.544 ms <br/> tps = 2554.829988 | latency = 120.572 ms <br/> tps = 1651.747017 |
| testdb3 | latency = 13.384 ms <br/> tps = 373.316920 | latency = 33.237 ms <br/> tps = 1501.470547 | latency = 125.518 ms <br/> tps = 1586.560109 |
| testdb4 | latency = 50.680 ms <br/> tps = 98.647159  | latency = 17.233 ms <br/> tps = 2894.750356 | latency = 78.069 ms <br/> tps = 2552.895607  |
| testdb5 | latency = 66.420 ms <br/> tps = 75.225301  | latency = 1359.517 ms <br/> tps = 35.077752 | latency = 53.236 ms <br/> tps = 3740.371668  |
| testdb6 | latency = 58.470 ms <br/> tps = 85.455958  | latency = 28.441 ms <br/> tps = 1756.255576 | latency = 22.256 ms <br/> tps = 8929.418574  |
| testdb7 | latency = 16.242 ms <br/> tps = 307.647725 | latency = 8.832 ms <br/> tps = 5639.845781  | latency = 44.660 ms <br/> tps = 4442.850159  |

</details>


<details>
<summary>-M = extended</summary>

|         | c = 5                                      | c = 50                                      | c = 200                                      |
|---------|--------------------------------------------|---------------------------------------------|----------------------------------------------|
| testdb1 | latency = 255.140 ms <br/> tps = 19.563055 | latency = 1023.533 ms <br/> tps = 47.672954 | latency = 473.056 ms <br/> tps = 417.678230  |
| testdb2 | latency = 4.198 ms <br/> tps = 1189.981434 | latency = 18.769 ms <br/> tps = 2658.254777 | latency = 135.183 ms <br/> tps = 1473.493170 |
| testdb3 | latency = 8.289 ms <br/> tps = 602.872182  | latency = 37.362 ms <br/> tps = 1336.553032 | latency = 171.264 ms <br/> tps = 1162.910434 |
| testdb4 | latency = 48.574 ms <br/> tps = 102.897826 | latency = 12.237 ms <br/> tps = 4073.767942 | latency = 86.256 ms <br/> tps = 2311.584731  |
| testdb5 | latency = 62.486 ms <br/> tps = 79.955803  | latency = 207.174 ms <br/> tps = 241.187998 | latency = 57.119 ms <br/> tps = 3486.329686  |
| testdb6 | latency = 61.956 ms <br/> tps = 80.612745  | latency = 6.705 ms <br/> tps = 7423.372557  | latency = 20.272 ms <br/> tps = 9799.330990  |
| testdb7 | latency = 2.089 ms <br/> tps = 2392.367388 | latency = 9.957 ms <br/> tps = 5004.640582  | latency = 47.133 ms <br/> tps = 4220.836972  |

</details>

<details>
<summary>-f custom_select.sql</summary>

|         | c = 5                                        | c = 50                                      |
|---------|----------------------------------------------|---------------------------------------------|
| testdb1 | latency = 28.063 ms <br/> tps = 178.087550   | latency = 257.989 ms <br/> tps = 193.515977 |
| testdb2 | latency = 442.874 ms <br/> tps = 11.227900   | latency = 4208.024 ms <br/> tps = 11.641320 |
| testdb3 | latency = 474.252 ms <br/> tps = 10.516530   | latency = 4689.654 ms <br/> tps = 10.368481 |
| testdb4 | latency = 160372.674 ms <br/> tps = 0.031131 | latency = 43305.817 ms <br/> tps = 1.149757 |
| testdb5 | latency = 175376.956 ms <br/> tps = 0.028509 | latency = 46344.840 ms <br/> tps = 1.061127 |
| testdb6 | latency = 237706.635 ms <br/> tps = 0.021020 | latency = 44538.393 ms <br/> tps = 1.111027 |
| testdb7 | latency = 5258.430 ms <br/> tps = 0.913652   | latency = 47619.364 ms <br/> tps = 1.036234 |

</details>

Полный отчет тестов представлен в файле [experiment 14](/exam/experiments/e_14.md).


### Эксперимент №15

В этом эксперименте вернёмся к настройкам эксперимента №2 для ВМ с SSD диском, уберём изменения по `synchronous_commit = off`, 
`fsync` и `full_page_writes` в `postgresql.conf` и отключим некоторые настройки для построения плана запроса. 

Поключим следующие настройки:
```
enable_sort = off    
enable_seqscan = off
enable_partition_pruning = off
enable_parallel_append = off
enable_parallel_hash = off
enable_nestloop = off
enable_bitmapscan = off
```

Полный конфиг файла `pgtune.conf` можно посмотреть в [Конфигуарция для эксперимента №15](/exam/configs.md#конфигуарция-для-эксперимента-15)

В результате были получены следующие данные:

<details>
<summary>-M = simple</summary>
</details>




Полный отчет тестов представлен в файле [experiment 15](/exam/experiments/e_15.md).


### Оценка времени между 2 и 14 экспериментами

-M = simple

|         | c = 5                                           | c = 50                                            | c = 200                                          |
|---------|-------------------------------------------------|---------------------------------------------------|--------------------------------------------------|
| testdb1 | latency = + 42.288 ms <br/> tps = - 559.579437  | latency = + 1809.044 ms <br/> tps = - 633.089342  | latency = + 5964.623 ms <br/> tps = - 483.261668 |
| testdb2 | latency = + 1.404 ms <br/> tps = - 303.635629   | latency = - 3.345 ms <br/> tps = + 375.504488     | latency = + 44.563 ms <br/> tps = - 972.037583   |
| testdb3 | latency = + 9.02 ms <br/> tps = - 771.485845    | latency = + 10.18 ms <br/> tps = - 663.368471     | latency = + 48.207 ms <br/> tps = - 991.132025   |
| testdb4 | latency = + 46.767 ms <br/> tps = - 1177.610181 | latency = + 4.994 ms <br/> tps = - 1175.528037    | latency = + 24.194 ms <br/> tps = - 1141.434561  |
| testdb5 | latency = + 53.855 ms <br/> tps = - 322.506942  | latency = + 1339.131 ms <br/> tps = - 2404.520508 | latency = - 5884.44 ms <br/> tps = + 3711.57497  |
| testdb6 | latency = + 52.441 ms <br/> tps = - 743.572298  | latency = + 23.351 ms <br/> tps = - 8007.606808   | latency = + 3.342 ms <br/> tps = - 1542.783161   |
| testdb7 | latency = + 15.699 ms <br/> tps = - 8861.785679 | latency = + 4.893 ms <br/> tps = - 6943.828489    | latency = + 24.939 ms <br/> tps = - 5606.158414  |


-M = extended

|         | c = 5                                           | c = 50                                           | c = 200                                           |
|---------|-------------------------------------------------|--------------------------------------------------|---------------------------------------------------|
| testdb1 | latency = + 247.669 ms <br/> tps = - 649.463708 | latency = + 943.387 ms <br/> tps = - 575.373283  | latency = + 10.716 ms <br/> tps = - 12.057385     |
| testdb2 | latency = + 0.301 ms <br/> tps = - 91.82658     | latency = + 0.221 ms <br/> tps = - 33.055367     | latency = + 60.111 ms <br/> tps = - 1182.348621   |
| testdb3 | latency = + 4.006 ms <br/> tps = - 563.43126    | latency = + 16.103 ms <br/> tps = - 1011.231807  | latency = + 94.969 ms <br/> tps = - 1443.85568    |
| testdb4 | latency = + 44.404 ms <br/> tps = - 1094.546626 | latency = - 1.968 ms <br/> tps = + 795.946987    | latency = + 40.101 ms <br/> tps = - 1997.249206   |
| testdb5 | latency = + 50.444 ms <br/> tps = - 335.009372  | latency = + 177.145 ms <br/> tps = - 1420.426243 | latency = - 4104.698 ms <br/> tps = + 3442.092358 |
| testdb6 | latency = + 61.199 ms <br/> tps = - 6509.1749   | latency = + 1.726 ms <br/> tps = - 2551.848887   | latency = - 0.095 ms <br/> tps = + 67.132424      |
| testdb7 | latency = + 1.465 ms <br/> tps = - 5591.254243  | latency = + 5.222 ms <br/> tps = - 5472.312594   | latency = + 24.163 ms <br/> tps = - 4404.016592   |


-f custom_select.sql

|         | c = 5                                            | c = 50                                          |
|---------|--------------------------------------------------|-------------------------------------------------|
| testdb1 | latency = - 31.544 ms <br/> tps = + 94.273582    | latency = - 286.678 ms <br/> tps = + 102.118959 |
| testdb2 | latency = - 131.898 ms <br/> tps = + 2.585552    | latency = - 776.524 ms <br/> tps = + 1.818116   |
| testdb3 | latency = - 133.48 ms <br/> tps = + 2.319149     | latency = - 836.862 ms <br/> tps = + 1.471896   |
| testdb4 | latency = + 154040.616 ms <br/> tps = - 0.718149 | latency = - 36207.34 ms <br/> tps = + 0.534889  |
| testdb5 | latency = + 142710.592 ms <br/> tps = - 0.117328 | latency = - 9255.577 ms <br/> tps = + 0.199043  |
| testdb6 | latency = + 232061.207 ms <br/> tps = - 0.8396   | latency = - 6154.794 ms <br/> tps = + 0.155802  |
| testdb7 | latency = - 552.701 ms <br/> tps = + 0.094566    | latency = - 8047.105 ms <br/> tps = + 0.162938  |





### Оценка времени между 10 и 15 экспериментами

-M = simple

-M = extended

-f custom_select.sql



### Оценка времени между 14 и 15 экспериментами

-M = simple

-M = extended

-f custom_select.sql





## Выводы

Следует также учитывать, что серия экспериментов в Яндекс Облаке была короткой, а у ВМ в Яндекс Облаке есть особенность, 
что работа ВМ может быть ниже в фолдере из-за других активных ВМ. Из-за этого наблюдается в некоторых тестах 
работа теста вместо 30 секунд по ~180-300.

1. Настройки pgtune значительно улучшают показатели работы любых тестируемых БД от pgbench.
2. Настройки autovacuum положительно сказываются на большие таблицы с партициями (s=100, partitions=20), 
негативно на все остальные.
3. autovacuum замедляет работу БД почти в 1.5-2 раза. При этом БД с партициями пострадали меньше или, наоборот, 
получили выигрыш по скорости.
4. В любых тестах с самой большим tps обладает БД 6 с unlogged tables или БД 7 (unlogged tables + partitions). 
После тюнинга, чаще БД 7 показывала результаты лучше, чем БД 6.
5. Ожидаемо, что все тесты на SSD в несколько раз быстрее, чем на HDD, потому что скорость I/O у SSD диска выше, 
чем у HDD, а это важно для БД.
6. SSD диск уменьшает значение `latency`.
7. Лучше всего SSD диск проявляет себя на больших данных (s=100) и большом кол-ве клиентов (c=200), чем HDD диск.
8. 



