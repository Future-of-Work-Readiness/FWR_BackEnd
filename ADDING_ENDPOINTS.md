# 🚀 Adding New Endpoints & Features Guide

This guide walks you through adding new API endpoints, database tables, and full CRUD operations in the Future Work Readiness Backend.

---

## 📁 Project Structure Overview

```
src/app/
├── main.py                    # Entry point (don't modify)
├── bootstrap.py               # App factory & router registration
├── config/
│   └── settings.py            # Environment settings
├── db/
│   ├── base.py                # SQLAlchemy Base class
│   ├── session.py             # Database connection
│   └── models.py              # ⭐ Central model registry
├── modules/
│   └── {your_module}/         # Feature modules
│       ├── __init__.py
│       ├── models.py          # Database tables
│       ├── schema.py          # Pydantic schemas (DTOs)
│       ├── service.py         # Business logic
│       └── router.py          # API endpoints
└── shared/
    └── schemas.py             # Shared schemas across modules
```

---

## 🎯 Quick Reference: What Goes Where

| What You Need | File Location |
|---------------|---------------|
| Database table | `src/app/modules/{module}/models.py` |
| Request/Response DTOs | `src/app/modules/{module}/schema.py` |
| Business logic | `src/app/modules/{module}/service.py` |
| API routes | `src/app/modules/{module}/router.py` |
| Register model for migrations | `src/app/db/models.py` |
| Register router | `src/app/bootstrap.py` |

---

## 📝 Step-by-Step: Adding a New Feature

Let's create a complete example: **Notifications Module** with full CRUD.

---

### Step 1: Create the Module Folder

```bash
mkdir -p src/app/modules/notifications
touch src/app/modules/notifications/__init__.py
touch src/app/modules/notifications/models.py
touch src/app/modules/notifications/schema.py
touch src/app/modules/notifications/service.py
touch src/app/modules/notifications/router.py
```

---

### Step 2: Define the Database Model

**File:** `src/app/modules/notifications/models.py`

```python
"""
Notification model.
Stores user notifications.
"""

import uuid
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class Notification(Base):
    """User notification model."""

    __tablename__ = "notifications"

    # Primary key - always use UUID with entity-specific name
    notification_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    # Notification fields
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # 'info', 'warning', 'success', 'error'
    is_read = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
```

#### 📌 Model Naming Conventions

| Convention | Example |
|------------|---------|
| Table name | `notifications` (plural, snake_case) |
| Primary key | `notification_id` (entity_id format, UUID) |
| Foreign key | `user_id` (references `users.user_id`) |
| Timestamps | `created_at`, `updated_at`, `deleted_at` |

---

### Step 3: Register the Model in Central Registry

**File:** `src/app/db/models.py`

Add your import at the bottom of the imports section:

```python
# ... existing imports ...

# Notification models
from src.app.modules.notifications.models import Notification

# Export all models
__all__ = [
    "Base",
    # ... existing models ...
    # Notifications
    "Notification",
]
```

⚠️ **This step is critical!** Without it:
- Alembic won't detect your table for migrations
- `Base.metadata.create_all()` won't create your table

---

### Step 4: Update Related Models (if needed)

If your model has relationships, update the related model.

**File:** `src/app/modules/users/models.py`

Add the back-reference relationship:

```python
class User(Base):
    # ... existing fields ...

    # Add relationship (at the bottom of the class)
    notifications = relationship("Notification", back_populates="user")
```

---

### Step 5: Create Pydantic Schemas

**File:** `src/app/modules/notifications/schema.py`

```python
"""
Notification schemas.
Pydantic models for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================================
# BASE SCHEMAS
# ============================================================

class NotificationBase(BaseModel):
    """Base schema with common fields."""
    title: str
    message: str
    notification_type: str = "info"


# ============================================================
# REQUEST SCHEMAS (for creating/updating)
# ============================================================

class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: UUID


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    is_read: Optional[bool] = None


# ============================================================
# RESPONSE SCHEMAS (for API responses)
# ============================================================

class NotificationResponse(NotificationBase):
    """Schema for notification response."""
    notification_id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enables ORM mode


class NotificationListResponse(BaseModel):
    """Schema for list of notifications."""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
```

#### 📌 Schema Naming Conventions

| Schema Type | Naming | Purpose |
|-------------|--------|---------|
| `{Entity}Base` | `NotificationBase` | Shared fields |
| `{Entity}Create` | `NotificationCreate` | POST request body |
| `{Entity}Update` | `NotificationUpdate` | PATCH/PUT request body |
| `{Entity}Response` | `NotificationResponse` | Single item response |
| `{Entity}ListResponse` | `NotificationListResponse` | List response |

---

### Step 6: Create the Service Layer

**File:** `src/app/modules/notifications/service.py`

```python
"""
Notification service.
Business logic for notification operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.app.modules.notifications.models import Notification
from src.app.modules.notifications.schema import NotificationCreate, NotificationUpdate


class NotificationService:
    """Service class for notification operations."""

    # ============================================================
    # CREATE
    # ============================================================

    @staticmethod
    def create_notification(db: Session, data: NotificationCreate) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            notification_type=data.notification_type,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    # ============================================================
    # READ
    # ============================================================

    @staticmethod
    def get_notification_by_id(
        db: Session,
        notification_id: UUID
    ) -> Optional[Notification]:
        """Get a single notification by ID."""
        return db.query(Notification).filter(
            Notification.notification_id == notification_id
        ).first()

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()

    @staticmethod
    def get_unread_count(db: Session, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        return db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()

    # ============================================================
    # UPDATE
    # ============================================================

    @staticmethod
    def mark_as_read(db: Session, notification_id: UUID) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id
        ).first()

        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: UUID) -> int:
        """Mark all notifications as read for a user. Returns count updated."""
        result = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        db.commit()
        return result

    # ============================================================
    # DELETE
    # ============================================================

    @staticmethod
    def delete_notification(db: Session, notification_id: UUID) -> bool:
        """Delete a notification. Returns True if deleted."""
        notification = db.query(Notification).filter(
            Notification.notification_id == notification_id
        ).first()

        if notification:
            db.delete(notification)
            db.commit()
            return True

        return False

    @staticmethod
    def delete_all_read(db: Session, user_id: UUID) -> int:
        """Delete all read notifications for a user. Returns count deleted."""
        result = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == True
            )
        ).delete()
        db.commit()
        return result
```

#### 📌 Service Layer Rules

- ✅ All database operations go here
- ✅ Use `@staticmethod` for stateless operations
- ✅ Accept `db: Session` as first parameter
- ✅ Return model objects or primitive types
- ❌ No HTTP exceptions (handle in router)
- ❌ No request/response objects

---

### Step 7: Create the Router (API Endpoints)

**File:** `src/app/modules/notifications/router.py`

```python
"""
Notification API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.notifications.service import NotificationService
from src.app.modules.notifications.schema import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
)

router = APIRouter()


# ============================================================
# CREATE
# ============================================================

@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification."""
    try:
        notification = NotificationService.create_notification(db, data)
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")


# ============================================================
# READ
# ============================================================

@router.get("/user/{user_id}", response_model=NotificationListResponse)
def get_user_notifications(
    user_id: UUID,
    unread_only: bool = Query(False, description="Filter to unread only"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all notifications for a user."""
    try:
        notifications = NotificationService.get_user_notifications(
            db, user_id, unread_only, limit, offset
        )
        unread_count = NotificationService.get_unread_count(db, user_id)

        return {
            "notifications": notifications,
            "total": len(notifications),
            "unread_count": unread_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific notification by ID."""
    notification = NotificationService.get_notification_by_id(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


# ============================================================
# UPDATE
# ============================================================

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = NotificationService.mark_as_read(db, notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.patch("/user/{user_id}/read-all")
def mark_all_as_read(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for a user."""
    count = NotificationService.mark_all_as_read(db, user_id)
    return {"message": f"Marked {count} notifications as read"}


# ============================================================
# DELETE
# ============================================================

@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a notification."""
    deleted = NotificationService.delete_notification(db, notification_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")

    return None  # 204 No Content


@router.delete("/user/{user_id}/read")
def delete_read_notifications(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete all read notifications for a user."""
    count = NotificationService.delete_all_read(db, user_id)
    return {"message": f"Deleted {count} read notifications"}
```

#### 📌 Router Rules

| HTTP Method | Use Case | Status Code |
|-------------|----------|-------------|
| `GET` | Retrieve data | 200 |
| `POST` | Create new resource | 201 |
| `PATCH` | Partial update | 200 |
| `PUT` | Full update | 200 |
| `DELETE` | Remove resource | 204 (no body) |

#### 📌 Route Ordering (Important!)

Always define routes in this order to avoid path parameter conflicts:

```python
# 1. Literal paths FIRST
@router.get("/stats")           # ✅ Literal - define first
@router.get("/summary")         # ✅ Literal - define first

# 2. Parameterized paths AFTER
@router.get("/{notification_id}")  # ✅ Parameter - define after literals
```

---

### Step 8: Update Module's `__init__.py`

**File:** `src/app/modules/notifications/__init__.py`

```python
"""
Notifications module.
Handles user notifications and alerts.
"""

from src.app.modules.notifications.models import Notification
from src.app.modules.notifications.service import NotificationService

__all__ = ["Notification", "NotificationService"]
```

---

### Step 9: Register the Router

**File:** `src/app/bootstrap.py`

Add the import and registration in the `_register_routers` function:

```python
def _register_routers(app: FastAPI) -> None:
    """Register all module routers."""
    from src.app.modules.users.router import router as users_router
    from src.app.modules.quizzes.router import router as quizzes_router
    from src.app.modules.sectors.router import router as sectors_router
    from src.app.modules.goals.router import router as goals_router
    from src.app.modules.admin.router import router as admin_router
    # 👇 Add your new router import
    from src.app.modules.notifications.router import router as notifications_router

    app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
    app.include_router(quizzes_router, prefix=f"{settings.API_V1_PREFIX}/quizzes", tags=["Quizzes"])
    app.include_router(sectors_router, prefix=f"{settings.API_V1_PREFIX}/sectors", tags=["Sectors"])
    app.include_router(goals_router, prefix=f"{settings.API_V1_PREFIX}/goals", tags=["Goals"])
    app.include_router(admin_router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
    # 👇 Add your new router registration
    app.include_router(notifications_router, prefix=f"{settings.API_V1_PREFIX}/notifications", tags=["Notifications"])
```

---

### Step 10: Create Database Migration

#### Option A: Auto-generate migration with Alembic

```bash
# Generate migration file
alembic revision --autogenerate -m "add_notifications_table"

# Review the generated migration in alembic/versions/
# Then apply it
alembic upgrade head
```

#### Option B: Let the app create tables automatically

If running with Docker, the app will auto-create tables on startup via `Base.metadata.create_all()`.

```bash
# Restart containers to pick up new models
docker-compose down && docker-compose up
```

---

## ✅ Verification Checklist

After adding your feature, verify:

- [ ] Model file created in `src/app/modules/{module}/models.py`
- [ ] Model imported in `src/app/db/models.py`
- [ ] Schema file created in `src/app/modules/{module}/schema.py`
- [ ] Service file created in `src/app/modules/{module}/service.py`
- [ ] Router file created in `src/app/modules/{module}/router.py`
- [ ] Router registered in `src/app/bootstrap.py`
- [ ] `__init__.py` updated with exports
- [ ] Migration created/run OR tables auto-created

---

## 🧪 Testing Your Endpoints

### Start the server

```bash
docker-compose up
```

### Access Swagger UI

Open [http://localhost:8000/docs](http://localhost:8000/docs) to see your new endpoints.

### Test with curl

```bash
# Create notification
curl -X POST http://localhost:8000/api/v1/notifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-uuid-here",
    "title": "Test Notification",
    "message": "This is a test",
    "notification_type": "info"
  }'

# Get user notifications
curl http://localhost:8000/api/v1/notifications/user/{user_id}

# Mark as read
curl -X PATCH http://localhost:8000/api/v1/notifications/{notification_id}/read

# Delete notification
curl -X DELETE http://localhost:8000/api/v1/notifications/{notification_id}
```

---

## 📚 Common Patterns

### Adding a Field to Existing Model

1. Add field to model in `src/app/modules/{module}/models.py`
2. Update schemas in `src/app/modules/{module}/schema.py`
3. Generate migration: `alembic revision --autogenerate -m "add_field_to_table"`
4. Apply migration: `alembic upgrade head`

### Adding a Relationship

1. Add foreign key column to child model
2. Add `relationship()` to both models
3. Register both models in `src/app/db/models.py`
4. Generate and apply migration

### Creating Admin Endpoints

Admin endpoints follow the same pattern but live in:
```
src/app/modules/admin/{feature}/
├── router.py
└── service.py
```

---

## 🚫 Common Mistakes to Avoid

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Forgetting to register model in `db/models.py` | Table not created | Add import to `src/app/db/models.py` |
| Forgetting to register router in `bootstrap.py` | Endpoints not accessible | Add to `_register_routers()` |
| Wrong route order (param before literal) | Routes not matched correctly | Define literal paths before parameterized |
| Business logic in router | Hard to test/maintain | Move to service layer |
| DB operations in router | Violates separation of concerns | Move to service layer |
| Using `id` instead of `{entity}_id` | Inconsistent naming | Use `notification_id`, `user_id`, etc. |

---

## 📋 File Templates

### Quick Copy-Paste Templates

<details>
<summary><b>Model Template</b></summary>

```python
"""
{Entity} model.
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.app.db.base import Base


class {Entity}(Base):
    __tablename__ = "{entities}"

    {entity}_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Add your fields here

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

</details>

<details>
<summary><b>Schema Template</b></summary>

```python
"""
{Entity} schemas.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class {Entity}Base(BaseModel):
    # Common fields
    pass


class {Entity}Create({Entity}Base):
    pass


class {Entity}Update(BaseModel):
    pass


class {Entity}Response({Entity}Base):
    {entity}_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
```

</details>

<details>
<summary><b>Service Template</b></summary>

```python
"""
{Entity} service.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.app.modules.{module}.models import {Entity}
from src.app.modules.{module}.schema import {Entity}Create


class {Entity}Service:

    @staticmethod
    def create(db: Session, data: {Entity}Create) -> {Entity}:
        entity = {Entity}(**data.model_dump())
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def get_by_id(db: Session, {entity}_id: UUID) -> Optional[{Entity}]:
        return db.query({Entity}).filter({Entity}.{entity}_id == {entity}_id).first()

    @staticmethod
    def get_all(db: Session, limit: int = 100, offset: int = 0) -> List[{Entity}]:
        return db.query({Entity}).offset(offset).limit(limit).all()

    @staticmethod
    def delete(db: Session, {entity}_id: UUID) -> bool:
        entity = db.query({Entity}).filter({Entity}.{entity}_id == {entity}_id).first()
        if entity:
            db.delete(entity)
            db.commit()
            return True
        return False
```

</details>

<details>
<summary><b>Router Template</b></summary>

```python
"""
{Entity} API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.app.db.session import get_db
from src.app.modules.{module}.service import {Entity}Service
from src.app.modules.{module}.schema import {Entity}Create, {Entity}Response

router = APIRouter()


@router.post("/", response_model={Entity}Response, status_code=201)
def create_{entity}(data: {Entity}Create, db: Session = Depends(get_db)):
    return {Entity}Service.create(db, data)


@router.get("/{{{entity}_id}}", response_model={Entity}Response)
def get_{entity}({entity}_id: UUID, db: Session = Depends(get_db)):
    entity = {Entity}Service.get_by_id(db, {entity}_id)
    if not entity:
        raise HTTPException(status_code=404, detail="{Entity} not found")
    return entity


@router.get("/", response_model=List[{Entity}Response])
def list_{entities}(db: Session = Depends(get_db)):
    return {Entity}Service.get_all(db)


@router.delete("/{{{entity}_id}}", status_code=204)
def delete_{entity}({entity}_id: UUID, db: Session = Depends(get_db)):
    if not {Entity}Service.delete(db, {entity}_id):
        raise HTTPException(status_code=404, detail="{Entity} not found")
    return None
```

</details>

---

## 🆘 Need Help?

If your endpoints aren't working:

1. Check the logs: `docker-compose logs -f backend`
2. Verify Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
3. Check model registration in `src/app/db/models.py`
4. Check router registration in `src/app/bootstrap.py`
5. Restart containers: `docker-compose restart backend`

