# Apna Store Backend

A production-ready FastAPI backend foundation built with Clean Architecture principles.

## 🚀 Features
- **FastAPI**: Modern, fast (high-performance) web framework.
- **SQLAlchemy**: Database toolkit and Object-Relational Mapper (ORM).
- **PostgreSQL**: Robust open-source relational database.
- **Pydantic Settings**: Environment variable management with type safety.
- **Automatic Table Creation**: Simplifies development by creating tables on startup.
- **Clean Architecture**: Modular structure for scalability and maintainability.

## 📁 Project Structure

```text
.
├── app/
│   ├── api/                # API Layer: Route handlers and versioning
│   │   ├── v1/             # Version 1 of the API
│   │   │   ├── api.py      # Entry point for v1 routes (aggregates all endpoint routers)
│   │   │   └── endpoints/  # Folder for specific route logic (e.g., users.py, items.py)
│   │   └── deps.py         # Dependencies: Reusable dependencies like `get_db` or `get_current_user`
│   ├── core/               # Core Layer: App-wide configurations and utilities
│   │   ├── config.py       # Pydantic Settings: Reads from .env and validates config
│   │   ├── database.py     # Database setup: Engine, SessionLocal, and Declarative Base
│   │   └── security.py     # Security helpers: JWT token creation, password hashing stubs
│   ├── models/             # Database Models: SQLAlchemy ORM models
│   │   ├── base.py         # Base model with common fields (ID, created_at, updated_at)
│   │   └── __init__.py     # Model discovery: Helps Python/SQLAlchemy find all models
│   ├── repository/         # Data Access Layer: CRUD operations and database queries
│   ├── schemas/            # Pydantic Schemas: Data validation and serialization (Request/Response bodies)
│   ├── services/           # Service Layer: Business logic that coordinates repositories and API
│   └── main.py             # App entry point: Initializes FastAPI, Middlewares (CORS), and Table Creation
├── .env                    # Environment variables (DB credentials, secret keys)
├── .env.example            # Template for .env (never contains real secrets)
├── .gitignore              # Files to ignore in Git (e.g., node_modules, .env, __pycache__)
└── requirements.txt        # Python library dependencies
```

## 🛠️ How it Works

### 1. Database & Models
- Models are defined in `app/models/`.
- `Base.metadata.create_all(bind=engine)` in `app/main.py` ensures that all models imported in `app/models/__init__.py` are created as tables in the database automatically on startup.

### 2. Dependency Injection
- Use `get_db` from `app/api/deps.py` in your routes to get an active database session.
- Example: `db: Session = Depends(get_db)`

### 3. Clean Architecture Flow
1. **API Interface**: Receives request inside `app/api/`.
2. **Service Layer**: Coordinates business rules in `app/services/`.
3. **Repository Layer**: Handles database interaction in `app/repository/`.
4. **Data Models**: Defined in `app/models/` and returned as `app/schemas/`.

## 🚦 Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Update `DATABASE_URL` with your local PostgreSQL credentials.

3. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **API Documentation**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
# store
