BEGIN;

-- Узнать количество учетных записей на ветку из pgbench_accounts для тех ветвей,
-- где баланс на уровне филиала больше нуля.
SELECT count(aid),a.bid FROM pgbench_accounts a JOIN pgbench_branches b ON a.bid = b.bid WHERE b.bbalance > 0 GROUP BY a.bid;

-- Узнать количество учетных записей на ветку из pgbench_accounts EXCEPT для тех ветвей,
-- где баланс на уровне ветви больше нуля.
SELECT count(aid),a.bid FROM pgbench_accounts a LEFT JOIN pgbench_branches b ON a.bid = b.bid AND b.bbalance > 0 WHERE b.bid IS NULL GROUP BY a.bid;

END;
