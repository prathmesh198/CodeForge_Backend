CREATE DATABASE IF NOT EXISTS codeforge;

USE codeforge;


-- ==========================================
-- USERS
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,

    username VARCHAR(50) NOT NULL UNIQUE,

    email VARCHAR(100) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- USER PROFILE
-- ==========================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,

    user_id INT NOT NULL UNIQUE,

    full_name VARCHAR(100),

    bio TEXT,

    profile_image VARCHAR(255),

    github_url VARCHAR(255),

    linkedin_url VARCHAR(255),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ==========================================
-- SUBMISSIONS
-- ==========================================

CREATE TABLE IF NOT EXISTS submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,

    user_id INT NOT NULL,

    problem_id INT NOT NULL,

    problem_title VARCHAR(200) NOT NULL,

    language VARCHAR(20) NOT NULL,

    code TEXT NOT NULL,

    status ENUM(
        'Accepted',
        'Wrong Answer',
        'Runtime Error',
        'Compilation Error',
        'Time Limit Exceeded',
        'Memory Limit Exceeded'
    ) NOT NULL,

    passed_tests INT DEFAULT 0,

    total_tests INT DEFAULT 0,

    runtime_ms INT DEFAULT NULL,

    memory_kb INT DEFAULT NULL,

    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ==========================================
-- INDEXES
-- ==========================================

CREATE INDEX idx_submissions_user
ON submissions(user_id);

CREATE INDEX idx_submissions_problem
ON submissions(problem_id);

CREATE INDEX idx_submissions_date
ON submissions(submitted_at);