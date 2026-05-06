# Hackathon Platform API

A backend REST API for managing hackathons built with FastAPI and MySQL.

## Tech Stack
- **Backend:** FastAPI (Python 3.12)
- **Database:** MySQL 9.6
- **Auth:** JWT + bcrypt

## Features
- User auth (register/login with JWT)
- Events management
- Team registration & management
- Project submissions
- Judge evaluations & leaderboard

## Setup

### 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/hackathon-platform.git
cd hackathon-platform

### 2. Create virtual environment
python -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials and secret key

### 5. Setup database
mysql -u root -p hackathon_db < schema.sql

### 6. Run the server
python -m uvicorn app.main:app --reload

## API Docs
Visit http://127.0.0.1:8000/docs after starting the server.

## Status
🚧 Work in progress — more features coming soon.
