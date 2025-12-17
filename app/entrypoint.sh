#!/bin/bash
set -e

echo "🚀 Starting Future Work Readiness Backend..."
echo "================================================"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
if [ -z "$DATABASE_URL" ]; then
  echo "❌ ERROR: DATABASE_URL environment variable is not set!"
  exit 1
fi

# Extract host from DATABASE_URL for psql connection check
# DATABASE_URL format: postgresql://user:password@host:port/database
until psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; do
  echo "  Database is unavailable - sleeping..."
  sleep 2
done

echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
cd /app && alembic upgrade head || echo "⚠️  Migration skipped (tables may already exist)"

# Create tables and seed database
echo "📊 Creating tables..."
python3 -c "
from app.core.database import Base, engine
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Tables created/verified')
"

# Run database seeding
echo "🌱 Auto-seeding database if empty..."
python3 -c "from app.seeds.base import auto_seed_if_empty; auto_seed_if_empty()"

# Start FastAPI server
echo "🚀 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
