#!/bin/bash
for (( number = 1; number <= 7; number++ ))
do
    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -U postgres testdb$number;
    sleep 5;
    echo; echo; echo;
    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -M extended -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -M extended -U postgres testdb$number
    sleep 5;
    echo; echo; echo;
    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -f /tmp/custom_select.sql -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 5 -j 2 -P 10 -T 30 -f /tmp/custom_select.sql -U postgres testdb$number
    sleep 5;
    echo; echo; echo;

    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -U postgres testdb$number;
    sleep 5;
    echo; echo; echo;
    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -M extended -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -M extended -U postgres testdb$number
    sleep 5;
    echo; echo; echo;
    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -f /tmp/custom_select.sql -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 50 -j 2 -P 10 -T 30 -f /tmp/custom_select.sql -U postgres testdb$number
    sleep 5;
    echo; echo; echo;

    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 200 -j 2 -P 10 -T 30 -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 200 -j 2 -P 10 -T 30 -U postgres testdb$number;
    sleep 5;
    echo; echo; echo;
    echo "$ sudo /usr/pgsql-14/bin/pgbench -c 200 -j 2 -P 10 -T 30 -M extended -U postgres testdb$number";
    sudo /usr/pgsql-14/bin/pgbench -c 200  -j 2 -P 10 -T 30 -M extended -U postgres testdb$number
    sleep 5;
    echo; echo; echo;

done


