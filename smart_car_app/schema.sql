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


-- slots → Stores parking slots & booking details.
-- users → Stores admin & user credentials.
-- payments → Stores UPI payment transactions.



-- MariaDB [smart_parking]> show tables;
-- +-------------------------+
-- | Tables_in_smart_parking |
-- +-------------------------+
-- | payments                |
-- | slots                   |
-- | users                   |
-- +-------------------------+
-- 3 rows in set (0.001 sec)

-- MariaDB [smart_parking]> describe slots;
-- +---------------+--------------+------+-----+---------+----------------+
-- | Field         | Type         | Null | Key | Default | Extra          |
-- +---------------+--------------+------+-----+---------+----------------+
-- | id            | int(11)      | NO   | PRI | NULL    | auto_increment |
-- | place         | varchar(10)  | NO   |     | NULL    |                |
-- | slot_name     | varchar(10)  | NO   | UNI | NULL    |                |
-- | is_available  | tinyint(1)   | YES  |     | 1       |                |
-- | booked_by     | varchar(100) | YES  |     | NULL    |                |
-- | booking_time  | datetime     | YES  |     | NULL    |                |
-- | sensor_status | tinyint(1)   | YES  |     | 0       |                |
-- +---------------+--------------+------+-----+---------+----------------+
-- 7 rows in set (0.001 sec)

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

-- MariaDB [smart_parking]> describe paymentsl
--     -> ^C
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

