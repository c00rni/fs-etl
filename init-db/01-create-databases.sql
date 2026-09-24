CREATE DATABASE IF NOT EXISTS sec_fillings_db;
USE sec_fillings_db;
CREATE TABLE IF NOT EXISTS filling (
    cik VARCHAR(20) PRIMARY KEY,
    title VARCHAR(255),
    form_type VARCHAR(255),
    company_name VARCHAR(255),
    link VARCHAR(500),
    filling_date DATE
);
