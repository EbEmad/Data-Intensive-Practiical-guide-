-- Debezium requires REPLICATION and SELECT on the database
-- Run as root (docker-entrypoint-initdb.d runs as root)
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'myuser'@'%';
GRANT SELECT ON ecom.* TO 'myuser'@'%';
FLUSH PRIVILEGES;

-- Table that will be captured (topic: mysql.ecom.users)
USE ecom;
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
