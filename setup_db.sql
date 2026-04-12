-- DrSeba Healthcare Platform - MySQL Database Setup
-- Execute this script as root to set up the database

-- Create the database
CREATE DATABASE IF NOT EXISTS drseba_healthcare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

--Create a dedicated user for this application
CREATE USER IF NOT EXISTS 'drseba_user'@'localhost' IDENTIFIED BY 'DrsebaPwd123!@#';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON drseba_healthcare.* TO 'drseba_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT USER FROM mysql.user WHERE USER='drseba_user';

SELECT 'Database setup completed successfully!' AS Status;