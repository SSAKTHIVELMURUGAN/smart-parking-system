CREATE TABLE slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    place VARCHAR(10) NOT NULL,
    slot_name VARCHAR(10) NOT NULL UNIQUE,
    is_available TINYINT(1) DEFAULT 1,
    booked_by VARCHAR(100) DEFAULT NULL,
    booking_time DATETIME DEFAULT NULL,
    sensor_status TINYINT(1) DEFAULT 0
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user', 'attendant') NOT NULL
);


CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slot_id INT NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    upi_id VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL DEFAULT 50.00,
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (slot_id) REFERENCES slots(id) ON DELETE CASCADE
);


-- MariaDB [smart_parking]> show tables;
-- +-------------------------+
-- | Tables_in_smart_parking |
-- +-------------------------+
-- | booking_details         |
-- | payments                |
-- | slots                   |
-- | users                   |
-- +-------------------------+


-- MariaDB [smart_parking]> describe booking_details;
-- +--------------------+--------------------+------+-----+---------------------+----------------+
-- | Field              | Type               | Null | Key | Default             | Extra          |
-- +--------------------+--------------------+------+-----+---------------------+----------------+
-- | id                 | int(11)            | NO   | PRI | NULL                | auto_increment |
-- | user_name          | varchar(100)       | NO   |     | NULL                |                |
-- | mobile_number      | varchar(15)        | NO   |     | NULL                |                |
-- | vehicle_type       | enum('Car','Bike') | NO   |     | NULL                |                |
-- | vehicle_number     | varchar(20)        | NO   |     | NULL                |                |
-- | slot_id            | int(11)            | NO   | MUL | NULL                |                |
-- | booking_start_time | datetime           | NO   |     | NULL                |                |
-- | booking_end_time   | datetime           | NO   |     | NULL                |                |
-- | booking_time       | timestamp          | NO   |     | current_timestamp() |                |
-- +--------------------+--------------------+------+-----+---------------------+----------------+
-- 9 rows in set (0.002 sec)

-- MariaDB [smart_parking]> describe slots;
-- +-----------------+--------------+------+-----+---------+----------------+
-- | Field           | Type         | Null | Key | Default | Extra          |
-- +-----------------+--------------+------+-----+---------+----------------+
-- | id              | int(11)      | NO   | PRI | NULL    | auto_increment |
-- | place           | varchar(10)  | NO   |     | NULL    |                |
-- | slot_name       | varchar(10)  | NO   | UNI | NULL    |                |
-- | is_available    | tinyint(1)   | YES  |     | 1       |                |
-- | booked_by       | varchar(100) | YES  |     | NULL    |                |
-- | booking_time    | datetime     | YES  |     | NULL    |                |
-- | sensor_status   | tinyint(1)   | YES  |     | 0       |                |
-- | checkout_status | tinyint(4)   | YES  |     | 0       |                |
-- +-----------------+--------------+------+-----+---------+----------------+
-- 8 rows in set (0.001 sec)

-- MariaDB [smart_parking]> describe users;
-- +----------+----------------------------------+------+-----+---------+----------------+
-- | Field    | Type                             | Null | Key | Default | Extra          |
-- +----------+----------------------------------+------+-----+---------+----------------+
-- | id       | int(11)                          | NO   | PRI | NULL    | auto_increment |
-- | username | varchar(50)                      | NO   | UNI | NULL    |                |
-- | password | varchar(255)                     | NO   |     | NULL    |                |
-- | role     | enum('admin','user','attendant') | NO   |     | NULL    |                |
-- +----------+----------------------------------+------+-----+---------+----------------+
-- 4 rows in set (0.001 sec)

-- MariaDB [smart_parking]> describe payments;
-- +--------------+---------------+------+-----+---------------------+----------------+
-- | Field        | Type          | Null | Key | Default             | Extra          |
-- +--------------+---------------+------+-----+---------------------+----------------+
-- | id           | int(11)       | NO   | PRI | NULL                | auto_increment |
-- | slot_id      | int(11)       | NO   | MUL | NULL                |                |
-- | user_name    | varchar(255)  | NO   |     | NULL                |                |
-- | upi_id       | varchar(255)  | NO   |     | NULL                |                |
-- | amount       | decimal(10,2) | NO   |     | 50.00               |                |
-- | payment_time | timestamp     | NO   |     | current_timestamp() |                |
-- +--------------+---------------+------+-----+---------------------+----------------+
-- 6 rows in set (0.002 sec)

-- MariaDB [smart_parking]> 


-- aDB [smart_parking]> select * from users;
-- +----+----------+--------------------------------------------------------------+-------+
-- | id | username | password                                                     | role  |
-- +----+----------+--------------------------------------------------------------+-------+
-- |  1 | user-1   | $2b$12$BbFCfrYibJ5JVGwm9aldfuONCggq64qUN/ntITVdt4q3fowSKwAv. | user  |
-- |  2 | user-2   | $2b$12$GMOeAm1L7cXSpZK7Z9IJ2u5EedSnjs.A6dfxJ9i0A28dqSfDiZSbG | user  |
-- |  3 | user1    | $2b$12$HCxs3mV5CjKqmz.p6J/lHubKjjUgX2nKYuBy1A8X/C8MQuWyynZNG | user  |
-- |  4 | sakthi   | $2b$12$HlfnAmNWIDWWUlIk79do0OTf/oiBBvx/ZIcxRQzz9eUQK4nZNiDye | user  |
-- |  5 | sakthi1  | sakthi1                                                      | admin |
-- +----+----------+--------------------------------------------------------------+-------+
-- 5 rows in set (0.001 sec)

-- MariaDB [smart_parking]> select * from slots;
-- +----+-------+-----------+--------------+-----------+---------------------+---------------+-----------------+
-- | id | place | slot_name | is_available | booked_by | booking_time        | sensor_status | checkout_status |
-- +----+-------+-----------+--------------+-----------+---------------------+---------------+-----------------+
-- |  1 | A     | A1        |            0 | sakthi1   | 2025-03-16 15:45:53 |             1 |               0 |
-- |  2 | A     | A2        |            0 | sakthi1   | 2025-03-17 09:15:15 |             1 |               0 |
-- |  3 | A     | A3        |            2 | NULL      | NULL                |             0 |               0 |
-- |  4 | B     | B1        |            0 | sakthi1   | 2025-03-17 10:06:17 |             1 |               0 |
-- |  5 | B     | B2        |            1 | NULL      | NULL                |             1 |               0 |
-- |  6 | B     | B3        |            2 | NULL      | NULL                |             0 |               0 |
-- +----+-------+-----------+--------------+-----------+---------------------+---------------+-----------------+
-- 6 rows in set (0.001 sec)

-- MariaDB [smart_parking]> select * from booking_details;
-- +----+-----------+---------------+--------------+----------------+---------+---------------------+---------------------+---------------------+
-- | id | user_name | mobile_number | vehicle_type | vehicle_number | slot_id | booking_start_time  | booking_end_time    | booking_time        |
-- +----+-----------+---------------+--------------+----------------+---------+---------------------+---------------------+---------------------+
-- |  1 | sakthi    | 1234567890    | Car          | TN 07 BN 1234  |       1 | 2025-03-13 12:55:00 | 2025-03-13 15:55:00 | 2025-03-13 12:55:38 |
-- |  2 | test1     | 1234567890    | Bike         | TN 10 TU 1234  |       2 | 2025-03-13 13:03:00 | 2025-03-13 17:02:00 | 2025-03-13 13:02:46 |
-- |  3 | test1     | 1234567890    | Bike         | TN 10 TU 1234  |       4 | 2025-03-13 13:03:00 | 2025-03-13 17:02:00 | 2025-03-13 13:06:23 |
-- |  4 | sakthi    | 1238344345    | Bike         | TN 32 BF 2342  |       5 | 2025-03-15 12:18:00 | 2025-03-15 18:12:00 | 2025-03-15 12:13:14 |
-- |  5 | sakthi1   | 1238344345    | Car          | TN 32 BF 2342  |       1 | 2025-03-15 13:22:00 | 2025-03-15 18:16:00 | 2025-03-15 13:16:15 |
-- |  6 | sakthi1   | 1234567890    | Car          | TN 01 BN 1234  |       1 | 2025-03-16 20:45:00 | 2025-03-16 15:51:00 | 2025-03-16 15:45:53 |
-- |  7 | sakthi1   | 1234567890    | Car          | TN 20 BN 2949  |       2 | 2025-03-17 09:21:00 | 2025-03-17 12:15:00 | 2025-03-17 09:15:15 |
-- |  8 | sakthi1   | 1234567890    | Car          | TN 93 BN 1244  |       4 | 2025-03-17 10:12:00 | 2025-03-17 15:06:00 | 2025-03-17 10:06:17 |
-- |  9 | sakthi1   | 1234567890    | Car          | TN 03 BN 1233  |       5 | 2025-03-17 11:29:00 | 2025-03-17 13:28:00 | 2025-03-17 11:28:46 |
-- +----+-----------+---------------+--------------+----------------+---------+---------------------+---------------------+---------------------+
-- 9 rows in set (0.001 sec)

-- MariaDB [smart_parking]> select * from payments;
-- +----+---------+-----------+---------------+--------+---------------------+
-- | id | slot_id | user_name | upi_id        | amount | payment_time        |
-- +----+---------+-----------+---------------+--------+---------------------+
-- |  1 |       4 | test      | example@paytm |  50.00 | 2025-03-12 00:38:23 |
-- |  2 |       4 | test      | example@paytm |  50.00 | 2025-03-12 00:42:35 |
-- |  3 |       5 | test2     | test2@upi     |  50.00 | 2025-03-12 00:43:06 |
-- |  4 |       5 | test2     | test2@upi     |  50.00 | 2025-03-12 00:45:48 |
-- |  7 |       1 | yogi      | yogi@upi      |  50.00 | 2025-03-12 23:44:51 |
-- |  8 |       1 | sakthi    | sakthi@upi    |  50.00 | 2025-03-13 12:56:00 |
-- |  9 |       1 | sakthi    | sakthi@upi    |  50.00 | 2025-03-13 12:57:22 |
-- | 10 |       4 | test2     | test2@upi     |  50.00 | 2025-03-13 13:06:34 |
-- | 11 |       5 | sakthi    | sakthi@upi    |  50.00 | 2025-03-15 12:13:49 |
-- | 12 |       1 | sakthi1   | sakthi@upi    |  50.00 | 2025-03-15 13:16:26 |
-- | 13 |       1 | sakthi1   | sakthi1@upi   |  50.00 | 2025-03-16 15:46:06 |
-- | 14 |       2 | sakthi1   | sakthi1@upi   |  50.00 | 2025-03-17 09:17:13 |
-- | 15 |       4 | sakthi1   | sakthi@upi    |  50.00 | 2025-03-17 10:06:29 |
-- | 16 |       5 | sakthi1   | sakthi1@upi   |  50.00 | 2025-03-17 11:28:59 |
-- +----+---------+-----------+---------------+--------+---------------------+
-- 14 rows in set (0.001 sec)

-- MariaDB [smart_parking]> 

