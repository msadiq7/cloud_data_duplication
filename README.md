Cloud Data Deduplication System

A web-based data deduplication system that validates incoming records, detects duplicate data, rejects invalid records, and stores only unique and verified records.

Project Overview

The Cloud Data Deduplication System is designed to reduce unnecessary duplicate data storage and maintain clean, reliable records.

Users can manually add records or upload multiple records through a CSV file. The system validates the submitted information and checks existing records before storing the data.

Features
Add new records
Validate user input
Email and phone number validation
Detect duplicate records
Reject duplicate records
Reject invalid records
Store only unique records
View all verified records
Delete records
Bulk CSV upload
Automatically skip duplicate CSV records
Automatically skip invalid CSV records
Dashboard statistics
Responsive web interface
Technology Stack
Frontend
HTML5
CSS3
JavaScript
Backend
Python
Flask
Database
SQLite for local development
Future Cloud Deployment
Cloud-hosted application
Cloud database
Production WSGI server
Project Structure
cloud-data-deduplication/
│
├── app.py
├── requirements.txt
├── deduplication.db
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
