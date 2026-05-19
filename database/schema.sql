-- Database schema for Resume Analyzer

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(10),
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE analysis (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL,
    ats_score FLOAT,
    skills TEXT,
    experience TEXT,
    education TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL,
    report_type VARCHAR(50),
    report_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);
