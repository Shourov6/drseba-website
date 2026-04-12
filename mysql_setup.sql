-- MySQL Setup Script for DrSeba Healthcare Platform
-- Run this script in MySQL to create the database and user

-- Create the database
CREATE DATABASE IF NOT EXISTS drseba_healthcare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user for this application (optional but recommended)
CREATE USER IF NOT EXISTS 'drseba_user'@'localhost' IDENTIFIED BY 'DrsebaPwd123!@#';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON drseba_healthcare.* TO 'drseba_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT USER FROM mysql.user WHERE USER='drseba_user';
