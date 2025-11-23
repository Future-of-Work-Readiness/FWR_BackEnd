# Future of Work Readiness Platform

A comprehensive career readiness assessment platform that helps users evaluate their skills and prepare for the future of work across various technology sectors and specializations.

## Features

- **Hierarchical Industry Structure**: Sectors → Branches → Specializations
- **Adaptive Assessments**: Multi-level difficulty quizzes for various specializations
- **User Progress Tracking**: Track readiness scores and quiz attempts
- **RESTful API**: FastAPI backend with full CRUD operations
- **Modern UI**: React frontend with responsive design

##Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
- **Node.js** (version 18+) and **npm** (version 9+)
- **Git**
- **(Optional) Python 3.9+** if you want to run backend locally without Docker

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/FutureWorkReadiness/FWR_BackEnd.git
cd FWR_BackEnd
```

### 2. Configure Environment Variables

#### Backend Configuration

Create a `.env` file in the root directory:

```bash
touch .env
```

Add the following content to `/.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://fw_user:fw_password_123@localhost:5432/futurework


### 3. Start the Application with Docker

#### Option A: Using Docker Compose (Recommended)

This will start all services (Database, Backend, Frontend) in containers:

```bash
# From the project root directory
docker-compose up -d
```

**What this does:**
- Starts PostgreSQL database on port 5432
-  Builds and starts FastAPI backend on port 8000
- Builds and starts React frontend on port 3000
- Automatically creates database tables and populates initial data

**Check container status:**
```bash
docker-compose ps
```

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove volumes (clean slate):**
```bash
docker-compose down -v
```

#### Option B: Run Services Individually

If you prefer more control:

```bash
# Start only the database
docker-compose up -d postgres

# Start backend (in a new terminal)
docker-compose up backend

# Start frontend (in another terminal)
docker-compose up frontend
```

### 4. Verify Installation

After starting the services, verify everything is running:

1. **Backend API Documentation**: http://localhost:8000/docs
2. **Frontend Application**: http://localhost:3000
3. **Database**: localhost:5432 (use any PostgreSQL client)

**Test the backend API:**
```bash
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{"status": "healthy", "database": "connected"}
```

## Running Locally (Without Docker)

### Backend Setup

```bash
# Navigate to backend directory
cd Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Install additional dependencies for quiz generation
pip install python-dotenv google-generativeai

# Ensure PostgreSQL is running (either via Docker or locally)
docker run -d \
  --name futurework_db \
  -e POSTGRES_USER=fw_user \
  -e POSTGRES_PASSWORD=fw_password_123 \
  -e POSTGRES_DB=futurework \
  -p 5432:5432 \
  postgres:15

# Create database tables
python3 -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(bind=engine)"

# Populate initial data
python3 -c "from app.db_init import auto_populate_if_empty; auto_populate_if_empty()"

# Start the FastAPI server
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```