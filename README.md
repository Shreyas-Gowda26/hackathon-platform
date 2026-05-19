# Hackathon Platform API

A backend REST API for managing hackathons — built with FastAPI and MySQL.

---

## Tech Stack

- **Backend:** FastAPI (Python 3.12)
- **Database:** MySQL 9.6
- **Auth:** JWT (Bearer Token) + bcrypt password hashing

---

## Base URL

```
http://127.0.0.1:8000
```

API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Authentication

This API uses **JWT Bearer Token** authentication.

1. Register or login to get a token
2. Pass the token in the `Authorization` header for protected routes:

```
Authorization: Bearer <your_token>
```

### User Roles

| Role | Access |
|---|---|
| `participant` | Register for events, create teams, submit projects |
| `mentor` | View assigned teams |
| `judge` | Evaluate projects |
| `admin` | Full access — create/delete events, assign mentors, manage registrations |

---

## Endpoints

### 🔐 Auth

#### Register
```
POST /auth/register
```
**Body:**
```json
{
  "name": "Shreyas",
  "email": "shreyas@gmail.com",
  "phone": "9999999999",
  "role": "participant",
  "password": "yourpassword"
}
```
**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

---

#### Login
```
POST /auth/login
```
**Body:**
```json
{
  "email": "shreyas@gmail.com",
  "password": "yourpassword"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "role": "participant",
  "user_id": 1
}
```

---

### 🎉 Events

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| `POST` | `/events/` | ✅ | admin |
| `GET` | `/events/` | ❌ | public |
| `GET` | `/events/{event_id}` | ❌ | public |
| `PUT` | `/events/{event_id}` | ✅ | admin |
| `DELETE` | `/events/{event_id}` | ✅ | admin |

#### Create Event
```
POST /events/
```
**Body:**
```json
{
  "event_name": "HackFest 2026",
  "description": "Annual hackathon",
  "start_date": "2026-06-01",
  "end_date": "2026-06-03",
  "max_team_size": 4,
  "min_team_size": 2
}
```

#### Update Event
```
PUT /events/{event_id}
```
**Body (all fields optional):**
```json
{
  "event_name": "HackFest 2026 Updated",
  "status": "ongoing"
}
```
> `status` can be: `upcoming` | `ongoing` | `completed`

---

### 📝 Registrations

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| `POST` | `/registrations/` | ✅ | any |
| `GET` | `/registrations/my` | ✅ | any |
| `GET` | `/registrations/event/{event_id}` | ✅ | admin |
| `PUT` | `/registrations/{registration_id}` | ✅ | admin |
| `DELETE` | `/registrations/{registration_id}` | ✅ | any |

#### Register for Event
```
POST /registrations/
```
**Body:**
```json
{
  "event_id": 1
}
```

#### Update Registration Status (Admin)
```
PUT /registrations/{registration_id}
```
**Body:**
```json
{
  "status": "confirmed"
}
```
> `status` can be: `pending` | `confirmed` | `cancelled`

---

### 👥 Teams

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| `POST` | `/teams/` | ✅ | any |
| `GET` | `/teams/event/{event_id}` | ❌ | public |
| `GET` | `/teams/{team_id}` | ❌ | public |
| `POST` | `/teams/{team_id}/members` | ✅ | team leader |
| `DELETE` | `/teams/{team_id}/members/{user_id}` | ✅ | team leader |

#### Create Team
```
POST /teams/
```
> Must be registered for the event first.
> Team creator automatically becomes the leader and first member.

**Body:**
```json
{
  "team_name": "Team Alpha",
  "event_id": 1
}
```

#### Add Member to Team
```
POST /teams/{team_id}/members
```
> Only team leader can add members. Respects max_team_size from event.

**Body:**
```json
{
  "user_id": 3
}
```

#### Get Team with Members
```
GET /teams/{team_id}
```
**Response:**
```json
{
  "team_id": 1,
  "team_name": "Team Alpha",
  "event_id": 1,
  "leader_id": 2,
  "members": [
    { "user_id": 2, "name": "Shreyas", "email": "...", "role": "participant" }
  ]
}
```

---

### 💡 Projects

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| `POST` | `/projects/` | ✅ | team leader |
| `GET` | `/projects/` | ❌ | public |
| `GET` | `/projects/{project_id}` | ❌ | public |
| `PUT` | `/projects/{project_id}` | ✅ | team leader |
| `DELETE` | `/projects/{project_id}` | ✅ | admin |

#### Create Project
```
POST /projects/
```
**Body:**
```json
{
  "team_id": 1,
  "title": "AI Crop Predictor",
  "description": "Predicts crop yield using ML",
  "repo_link": "https://github.com/...",
  "demo_link": "https://demo.example.com"
}
```

#### Submit Project
```
PUT /projects/{project_id}
```
**Body:**
```json
{
  "status": "submitted"
}
```
> `status` can be: `draft` | `submitted`
> Setting `submitted` automatically records the `submission_time`.

---

### 🧑‍🏫 Mentors

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| `POST` | `/mentors/assign` | ✅ | admin |
| `DELETE` | `/mentors/remove` | ✅ | admin |
| `GET` | `/mentors/team/{team_id}` | ❌ | public |
| `GET` | `/mentors/my-teams` | ✅ | mentor |
| `GET` | `/mentors/mentor/{mentor_id}` | ✅ | admin |

#### Assign Mentor to Team
```
POST /mentors/assign
```
> User must have role `mentor` to be assigned. Admin only.

**Body:**
```json
{
  "mentor_id": 2,
  "team_id": 1
}
```
**Response:**
```json
{
  "message": "Mentor assigned successfully",
  "id": 1
}
```

#### Remove Mentor from Team
```
DELETE /mentors/remove
```
**Body:**
```json
{
  "mentor_id": 2,
  "team_id": 1
}
```

#### Get All Mentors for a Team
```
GET /mentors/team/{team_id}
```
**Response:**
```json
[
  {
    "user_id": 2,
    "name": "John",
    "email": "john@gmail.com",
    "phone": "9999999999"
  }
]
```

#### Get My Assigned Teams (Mentor)
```
GET /mentors/my-teams
```
**Response:**
```json
[
  {
    "team_id": 1,
    "team_name": "Team Alpha",
    "event_name": "HackFest 2026",
    "start_date": "2026-06-01",
    "end_date": "2026-06-03",
    "leader_name": "Shreyas"
  }
]
```

#### Get All Teams of a Mentor (Admin)
```
GET /mentors/mentor/{mentor_id}
```

---

### ⚖️ Evaluations

| Method | Endpoint | Auth | Role |
|---|---|---|---|
| `POST` | `/evaluations/` | ✅ | judge |
| `GET` | `/evaluations/project/{project_id}` | ✅ | admin, judge |
| `GET` | `/evaluations/project/{project_id}/average` | ❌ | public |
| `PUT` | `/evaluations/{evaluation_id}` | ✅ | judge |
| `GET` | `/evaluations/leaderboard/{event_id}` | ❌ | public |

#### Evaluate a Project
```
POST /evaluations/
```
> Only users with role `judge` can evaluate.
> A judge can only evaluate each project once.
> Score must be between 0 and 100.

**Body:**
```json
{
  "project_id": 1,
  "score": 85,
  "feedback": "Great idea, clean execution."
}
```

#### Get Leaderboard for Event
```
GET /evaluations/leaderboard/{event_id}
```
**Response:**
```json
[
  {
    "team_name": "Team Alpha",
    "project_title": "AI Crop Predictor",
    "average_score": 91.5,
    "total_judges": 3,
    "repo_link": "https://github.com/...",
    "demo_link": "https://demo.example.com"
  }
]
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

| Status Code | Meaning |
|---|---|
| `400` | Bad request (duplicate, invalid data) |
| `401` | Unauthorized (missing or invalid token) |
| `403` | Forbidden (wrong role) |
| `404` | Resource not found |
| `422` | Validation error (wrong input format) |

---

## Setup (for local development)

```bash
# 1. Clone the repo
git clone https://github.com/Shreyas-Gowda26/hackathon-platform.git
cd hackathon-platform

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your MySQL credentials

# 5. Setup database
mysql -u root -p hackathon_db < schema.sql

# 6. Start the server
python -m uvicorn app.main:app --reload
```

---

## Project Structure

```
hackathon-platform/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # MySQL connection pool
│   ├── routes/
│   │   ├── auth.py          # Register & Login
│   │   ├── events.py        # Events CRUD
│   │   ├── registrations.py # Event registrations
│   │   ├── teams.py         # Teams & members
│   │   ├── projects.py      # Project submissions
│   │   ├── evaluations.py   # Judging & leaderboard
│   │   ├── mentors.py       # Mentor assignments
│   │   └── dependencies.py  # JWT auth middleware
│   └── schemas/
│       ├── user.py
│       ├── event.py
│       ├── registration.py
│       ├── team.py
│       ├── project.py
│       ├── evaluation.py
│       └── mentor.py
├── schema.sql               # Database schema
├── requirements.txt
├── .env.example
└── README.md
```

---

## Status

✅ Backend complete — all core APIs implemented.
