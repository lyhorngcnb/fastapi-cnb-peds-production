# FastAPI Property Evaluation System with RBAC

A professional, scalable FastAPI application built with clean architecture principles for property evaluation and loan management.

## 🏗️ Architecture Overview

This project follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── api/                    # API Layer (HTTP endpoints)
│   ├── routes/            # Route definitions
│   │   └── v1/           # API version 1 routes
│   │       ├── auth.py   # Authentication endpoints
│   │       └── customers.py # Customer management
├── core/                  # Core Application Layer
│   ├── config.py         # Configuration management
│   ├── dependencies.py   # FastAPI dependencies
│   ├── exceptions.py     # Custom exception classes
│   └── middleware.py     # Custom middleware
├── domain/               # Domain Layer (Business Models)
│   ├── customer.py       # Customer domain model
│   ├── loan_request.py   # Loan request model
│   └── ...               # Other domain models
├── infrastructure/       # Infrastructure Layer
│   └── database.py      # Database configuration
├── repositories/         # Data Access Layer
│   ├── base.py          # Base repository
│   └── customer_repository.py # Customer-specific operations
├── schemas/              # Data Transfer Objects
│   ├── base.py          # Base schemas
│   ├── auth.py          # Authentication schemas
│   └── customer.py      # Customer schemas
└── services/             # Business Logic Layer
    ├── base.py          # Base service
    └── customer_service.py # Customer business logic
```

## ✨ Key Features

- **🔐 RBAC Authentication**: Role-based access control with JWT tokens
- **🏗️ Clean Architecture**: Separation of concerns with dependency injection
- **📝 Type Safety**: Full Pydantic schema validation
- **🔄 Async Support**: Modern async/await patterns
- **📊 Database**: SQLAlchemy ORM with MySQL support
- **🛡️ Security**: Custom middleware, CORS, and security headers
- **📈 Monitoring**: Request logging and performance tracking
- **🧪 Testing Ready**: Structured for comprehensive testing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL database
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-cnb-peds-development
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file:
   ```env
   # Database
   DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
   
   # Security
   SECRET_KEY=your-super-secret-key-here
   
   # MinIO (File Storage)
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📚 API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /login` - User login
- `POST /register` - User registration
- `GET /me` - Get current user info
- `POST /change-password` - Change password
- `POST /refresh` - Refresh access token

### Customers (`/api/v1/customers`)
- `GET /` - List customers (with pagination & filtering)
- `POST /` - Create new customer
- `GET /{id}` - Get customer by ID
- `PUT /{id}` - Update customer
- `DELETE /{id}` - Delete customer

## 🔧 Configuration

The application uses Pydantic settings for configuration management. Key settings:

```python
# app/core/config.py
class Settings(BaseSettings):
    app_name: str = "FastAPI Property Evaluation System"
    database_url: str = "mysql+pymysql://user:password@localhost/dbname"
    secret_key: str = "your-secret-key-here"
    # ... more settings
```

## 🧪 Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🐳 Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

## 📖 Development

### Adding New Features

1. **Create Schema** (`app/schemas/`)
   ```python
   class NewFeatureSchema(BaseSchema):
       name: str
       description: Optional[str] = None
   ```

2. **Create Repository** (`app/repositories/`)
   ```python
   class NewFeatureRepository(BaseRepository[NewFeature, NewFeatureCreate, NewFeatureUpdate]):
       def custom_method(self, db: Session):
           # Custom data access logic
           pass
   ```

3. **Create Service** (`app/services/`)
   ```python
   class NewFeatureService(BaseService[NewFeature, NewFeatureCreate, NewFeatureUpdate]):
       def __init__(self):
           super().__init__(NewFeatureRepository())
   ```

4. **Create API Routes** (`app/api/routes/v1/`)
   ```python
   @router.post("/", response_model=NewFeatureResponse)
   async def create_feature(
       data: NewFeatureCreate,
       db: Session = Depends(get_db),
       current_user: User = Depends(require_permission("feature:create"))
   ):
       # Implementation
       pass
   ```

### Database Migrations

The application uses SQLAlchemy with automatic table creation. For production:

1. Use Alembic for migrations
2. Set up proper database backup strategies
3. Implement connection pooling

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **RBAC**: Role-based access control with granular permissions
- **Input Validation**: Pydantic schema validation
- **Security Headers**: XSS protection, content type options
- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: Ready for implementation

## 📊 Monitoring & Logging

- **Request Logging**: All requests are logged with timing
- **Error Tracking**: Comprehensive exception handling
- **Performance Metrics**: Request processing time headers
- **Health Checks**: Built-in health monitoring endpoint

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper type hints
3. Include docstrings for all functions
4. Write tests for new features
5. Update documentation

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

**Built with ❤️ using FastAPI and Clean Architecture principles** 