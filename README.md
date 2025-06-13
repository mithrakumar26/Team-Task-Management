# 🧑‍💼 Team Task Management System

A backend-focused team task management system built with **FastAPI** and **PostgreSQL**, featuring **JWT authentication** and **role-based access control**.

## 🚀 Features

### 👑 Admin
- Create, update, and delete projects
- Assign tasks to users with title, description, deadline, priority, and status
- View comments and task updates

### 🙋‍♂️ User
- Register and log in
- View assigned tasks
- Update task status (`pending`, `in_progress`, `completed`)
- Add comments to tasks

## 🔐 Tech Stack
- **Backend:** FastAPI + SQLAlchemy
- **Database:** PostgreSQL
- **Auth:** JWT (via `fastapi-jwt-auth`)
- **Password Hashing:** bcrypt
- **Frontend:** Streamlit (optional UI)

## 🛠️ Setup

1. Configure `.env` for DB and JWT
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
