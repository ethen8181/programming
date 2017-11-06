-- Question 1
-- How to find count of second degree followers
-- https://stackoverflow.com/questions/34431957/how-to-find-count-of-second-degree-followers-in-a-database-as-below
SELECT
    f1.followee AS f1_followee,
    COUNT(DISTINCT f2.follower) AS num
FROM
    following f1
INNER JOIN
    following f2
ON
    f1.follower = f2.followee
GROUP BY
    f1.followee


-- Question 2
-- Given timestamps, userid, how to determine the number of users who are active everyday in a week?
-- https://stackoverflow.com/questions/32840887/count-active-users-using-login-timestamp-in-mysql

-- provide the list of users, and the days they log in on, without duplicates
-- the where clause filters out record for this particular week and is excluded from
-- the rest of the query to not clutter it
SELECT
    DISTINCT user_id,
    DATE_FORMAT(login_timestamp, "%Y-%m-%d")
FROM
    logins
WHERE
    login_timestamp
BETWEEN
    DATE_FORMAT(ADDDATE(CURDATE(), INTERVAL 1 - DAYOFWEEK(CURDATE()) DAY), "%Y-%m-%d 00:00:00")
AND
    DATE_FORMAT(ADDDATE(CURDATE(), INTERVAL 7 - DAYOFWEEK(CURDATE()) DAY), "%Y-%m-%d 23:59:59")

-- log in count per user
SELECT
    logins.user_id,
    COUNT(*) AS login_count
FROM 
    (SELECT
        DISTINCT user_id,
        DATE_FORMAT(login_timestamp, "%Y-%m-%d")
    FROM
        logins) AS logins
GROUP BY
    logins.user_id

-- filter out people who didn't login for 7 times
SELECT
    user_id
FROM
    (SELECT
        logins.user_id,
        COUNT(*) AS login_count
    FROM 
        (SELECT
            DISTINCT user_id,
            DATE_FORMAT(login_timestamp, "%Y-%m-%d")
        FROM
            logins) AS logins
    GROUP BY
        logins.user_id) AS user_login_count
WHERE user_login_counts.login_count > 6


-- Question 3
-- Returns the name, phone number and most recent date for any user that
-- has logged in over the last 30 days (you can tell a user has logged in
-- if the action field in UserHistory is set to "logged_on").
-- http://www.programmerinterview.com/index.php/database-sql/practice-interview-question-2/
SELECT
    u.name,
    u.phone_num,
    MAX(h.date) AS recent
FROM
    UserHistory AS h
INNER JOIN
    User AS u
USING
    (user_id)
WHERE
    h.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND h.action = "logged_on"
GROUP BY
    u.name,
    u.phone_num


-- Question 4
-- Given the tables above, write a SQL query to determine which user_ids in the User table
-- are not contained in the UserHistory table (assume the UserHistory table has a subset of
-- the user_ids in User table). Do not use the SQL MINUS statement. Note: the UserHistory
-- table can have multiple entries for each user_id.
SELECT DISTINCT
    u.user_id
FROM
    User AS u
LEFT JOIN
    UserHistory AS h
USING
    user_id
WHERE
    u.user_id IS NULL


-- Question 5
-- find the largest order amount for each salesperson and the
-- associated order number, along with the customer to whom that
-- order belongs to.
-- http://www.programmerinterview.com/index.php/database-sql/advanced-sql-interview-questions-continued-part-2/
SELECT
    o.salesperson_id,
    s.Name AS salesperson_name,
    o.Number AS order_num,
    o.amount
FROM
    Orders AS o
INNER JOIN
    Salesperson AS s
ON
    s.ID = o.salesperson_id
INNER JOIN 
    (SELECT
        salesperson_id, MAX(Amount) AS max_order
    FROM
        Orders
    GROUP BY
        salesperson_id) AS TopOrderPerSalesperson
USING
    (salesperson_id)
WHERE
    Amount = TopOrderPerSalesperson.max_order
GROUP BY
    salesperson_id, salesperson_name, order_num, amount


-- Question 6
-- https://blog.statsbot.co/sql-queries-for-funnel-analysis-35d5e456371d
-- find out how many users connected at least one integration.
SELECT
    COUNT(*) AS count
FROM
    bots
WHERE
    (SELECT
        COUNT(*)
    FROM
        intergrations
    WHERE
        intergrations.bot_id = bots.id) > 0 AND
    created_at BETWEEN "2017-05-01" AND "2017-05-31"


-- Question 7
-- Write a sql query to find out the overall friend acceptance rate for a given date?
-- Table :- User_id_who_sent|User_id_to_whom|date|Action (Sent, accepted, rejected etc)
-- https://www.glassdoor.com/Interview/Write-a-sql-query-to-find-out-the-overall-friend-acceptance-rate-for-a-given-date-Table-User-id-who-sent-User-id-to-wh-QTN_2241356.htm
SELECT
    user_sent.User_id_who_sent,
    ISNULL(user_accepted.accepts, 0.0) * 1.0 / user_sent.sends AS rate
FROM
    (SELECT
        User_id_who_sent,
        COUNT(*) AS sends
    FROM
        requests
    WHERE
        action = "send"
    GROUP BY
        User_id_who_sent) AS user_sent
LEFT JOIN
    (SELECT
        User_id_who_sent,
        COUNT(*) AS accepts
    FROM
        requests
    WHERE
        action = "accepted"
    GROUP BY
        User_id_who_sent) AS user_accepted
ON
    user_sent.User_id_who_sent = user_accepted.User_id_who_sent
