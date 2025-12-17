# Future of Work Readiness Platform - Backend

A comprehensive career readiness assessment platform that helps users evaluate their skills and prepare for the future of work across various technology sectors and specializations.

## Features

- **Hierarchical Industry Structure**: Sectors → Branches → Specializations
- **Adaptive Assessments**: Multi-level difficulty quizzes for various specializations
- **User Progress Tracking**: Track readiness scores and quiz attempts
- **RESTful API**: FastAPI backend with full CRUD operations
- **Peer Benchmarking**: Compare your progress with peers
- **Goals & Journal**: Set goals and track your learning journey
- **Versioned API**: Clean `/api/v1` prefix for all endpoints

## Prerequisites

- **Python 3.9+** (3.11 recommended)
- **PostgreSQL 15+** (or Docker)
- **Git**

---

## 🚀 Quick Start (Docker - Recommended)

The easiest way to run the project is with Docker:

```bash
# 1. Clone the repository
git clone https://github.com/FutureWorkReadiness/FWR_BackEnd.git
cd FWR_BackEnd

# 2. Start all services
docker-compose up -d --build

# 3. Check status
docker-compose ps

# 4. View logs
docker-compose logs -f backend
```

**Access the API:**

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- API v1 endpoints: http://localhost:8000/api/v1/...

**Stop services:**

```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop and remove volumes (clean slate)
```

---

## 🔧 Local Development Setup (Without Docker)

Follow these steps to run the project locally from scratch.

### Step 1: Clone the Repository

```bash
git clone https://github.com/FutureWorkReadiness/FWR_BackEnd.git
cd FWR_BackEnd
```

### Step 2: Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

**Option A: Using Docker for PostgreSQL only (Recommended)**

```bash
# Start PostgreSQL container
docker run -d \
  --name futurework_db \
  -e POSTGRES_USER=fw_user \
  -e POSTGRES_PASSWORD=fw_password_123 \
  -e POSTGRES_DB=futurework \
  -p 5432:5432 \
  postgres:15

# Verify it's running
docker ps | grep futurework_db
```

**Option B: Using Local PostgreSQL Installation**

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database and user
psql postgres << EOF
CREATE USER fw_user WITH PASSWORD 'fw_password_123';
CREATE DATABASE futurework OWNER fw_user;
GRANT ALL PRIVILEGES ON DATABASE futurework TO fw_user;
EOF
```

**Option B (continued): Linux (Ubuntu/Debian)**

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE USER fw_user WITH PASSWORD 'fw_password_123';
CREATE DATABASE futurework OWNER fw_user;
GRANT ALL PRIVILEGES ON DATABASE futurework TO fw_user;
EOF
```

### Step 5: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file (optional - defaults work for local development)
# The default DATABASE_URL is: postgresql://fw_user:fw_password_123@localhost:5432/futurework
```

**Verify your `.env` file contains:**

```env
DATABASE_URL=postgresql://fw_user:fw_password_123@localhost:5432/futurework
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true
```

### Step 6: Create Database Tables

```bash
# Run Alembic migrations
alembic upgrade head

# Or create tables directly
python3 -c "from app.core.database import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine); print('✅ Tables created')"
```

> **⚠️ Note about UUID Migration**: The database uses UUID primary keys for all tables. If upgrading from an older version with integer IDs, you must drop all existing tables first:
> ```bash
> # WARNING: This will delete ALL data
> alembic downgrade base
> alembic upgrade head
> python3 seed_database.py --force
> ```

### Step 7: Seed the Database

```bash
# Auto-seed with initial data from data/*.json files
python3 seed_database.py

# Or seed specific data
python3 seed_database.py sectors    # Seed sectors only
python3 seed_database.py quizzes    # Seed quizzes only
python3 seed_database.py --force    # Force re-seed (add missing data)
```

### Step 8: Start the Development Server

```bash
# Start FastAPI with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 9: Verify Installation

Open your browser and visit:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

**Test with curl:**

```bash
# Health check
curl http://localhost:8000/health

# Get all sectors
curl http://localhost:8000/api/v1/sectors

# Get all quizzes
curl http://localhost:8000/api/v1/quizzes
```

---

## 📁 Project Structure

```
FWR_BackEnd/
├── app/
│   ├── api/                      # API endpoints
│   │   └── v1/                   # Version 1 API
│   │       ├── __init__.py       # Exports api_router
│   │       ├── router.py         # API router aggregator
│   │       ├── users.py          # User authentication & profiles
│   │       ├── quizzes.py        # Quiz management & attempts
│   │       ├── sectors.py        # Sector hierarchy endpoints
│   │       ├── goals.py          # Goals & journal entries
│   │       └── admin.py          # Admin management endpoints
│   ├── core/                     # Core infrastructure
│   │   ├── config.py             # Application settings (env vars)
│   │   └── database.py           # SQLAlchemy engine & sessions
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py           # Exports all models
│   │   ├── user.py               # User model
│   │   ├── sector.py             # Sector, Branch, Specialization
│   │   ├── quiz.py               # Quiz, Question, QuestionOption
│   │   ├── goal.py               # Goal, JournalEntry
│   │   ├── badge.py              # Badge, UserBadge
│   │   └── benchmark.py          # PeerBenchmark
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py           # Exports all schemas
│   │   ├── user.py
│   │   ├── sector.py
│   │   ├── quiz.py
│   │   ├── goal.py
│   │   ├── benchmark.py
│   │   └── common.py
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py           # Exports all services
│   │   ├── user_service.py
│   │   ├── quiz_service.py
│   │   ├── sector_service.py
│   │   ├── goal_service.py
│   │   └── benchmark_service.py
│   ├── seeds/                    # Database seeding
│   │   ├── base.py               # Seed utilities & auto-seed
│   │   ├── seed_sectors.py       # Seed sectors from JSON
│   │   └── seed_quizzes.py       # Seed quizzes from JSON
│   ├── main.py                   # FastAPI app entry point
│   └── entrypoint.sh             # Docker entrypoint script
├── data/                         # Source data (JSON files)
│   ├── sectors.json              # Sector hierarchy data
│   └── quizzes.json              # Quiz questions data
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration scripts
│   └── env.py                    # Alembic configuration
├── seed_database.py              # CLI tool for manual seeding
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Docker build configuration
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🔧 Common Commands

### Local Development

```bash
# Start server with hot reload
uvicorn app.main:app --reload --port 8000

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Seed database
python3 seed_database.py

# Run tests
pytest
```

### Docker Commands

```bash
# Start all services
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend

# Access backend container shell
docker exec -it futurework_backend bash

# Access database
docker exec -it futurework_db psql -U fw_user -d futurework

# Rebuild after code changes
docker-compose up -d --build
```

---

## 🌐 API Endpoints

### API Version 1 (`/api/v1`)

| Endpoint                               | Method   | Description             |
| -------------------------------------- | -------- | ----------------------- |
| `/api/v1/users/register`               | POST     | Register new user       |
| `/api/v1/users/login`                  | POST     | User login              |
| `/api/v1/users/{id}`                   | GET      | Get user by ID          |
| `/api/v1/users/{id}/dashboard`         | GET      | Get user dashboard      |
| `/api/v1/sectors`                      | GET      | Get all sectors         |
| `/api/v1/sectors/hierarchy`            | GET      | Get full hierarchy      |
| `/api/v1/quizzes`                      | GET      | Get all quizzes         |
| `/api/v1/quizzes/{id}`                 | GET      | Get quiz with questions |
| `/api/v1/quizzes/{id}/start`           | POST     | Start quiz attempt      |
| `/api/v1/quizzes/attempts/{id}/submit` | POST     | Submit answers          |
| `/api/v1/goals`                        | GET/POST | User goals              |
| `/api/v1/goals/journal`                | GET/POST | Journal entries         |
| `/api/v1/admin/stats`                  | GET      | Database statistics     |

**Full API documentation available at:** http://localhost:8000/docs

---

## 🔒 Environment Variables

| Variable       | Description                  | Default             |
| -------------- | ---------------------------- | ------------------- |
| `DATABASE_URL` | PostgreSQL connection string | Required            |
| `SECRET_KEY`   | JWT signing key              | `dev-secret-key...` |
| `ENVIRONMENT`  | Environment name             | `development`       |
| `DEBUG`        | Enable debug mode            | `true`              |

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running (Docker)
docker ps | grep futurework_db

# Check PostgreSQL logs
docker logs futurework_db

# Test connection
PGPASSWORD=fw_password_123 psql -h localhost -U fw_user -d futurework -c "SELECT 1"
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Import Errors

```bash
# Ensure you're in the project root
cd /path/to/FWR_BackEnd

# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Reset

```bash
# Stop containers and remove volumes
docker-compose down -v

# Restart fresh
docker-compose up -d --build
```

---

## 📊 Database Schema

The platform uses a hierarchical structure:

```
Sectors (e.g., Technology)
└── Branches (e.g., Software Development)
    └── Specializations (e.g., Frontend Development)
        └── Quizzes (difficulty levels 1-5)
            └── Questions (multiple choice)
                └── Options (A, B, C, D)
```

---

## 🚀 Production Deployment

For production:

1. Change `SECRET_KEY` to a secure random value
2. Set `DEBUG=false`
3. Set `ENVIRONMENT=production`
4. Use a production-grade PostgreSQL instance
5. Set up SSL/HTTPS
6. Configure proper CORS origins
7. Use gunicorn instead of uvicorn:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License.
