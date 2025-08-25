import pytest
import asyncio
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.domain.rbac_models import User, Role, Permission, UserRole, RolePermission
from app.domain.customer import Customer
from app.domain.loan_request import LoanRequest
from app.domain.reference_models import Branch, LoanType, RequestType
from app.domain.property_models import Property, LandDetail, BuildingDetail, GoogleMap, Document
from app.domain.location_models import Province, District, Commune, Village, Agency

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Test data fixtures
@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data for creating users."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "is_active": True
    }

@pytest.fixture
def test_customer_data() -> Dict[str, Any]:
    """Test customer data for creating customers."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "date_of_birth": "1990-01-01",
        "national_id": "123456789",
        "address": "123 Test Street",
        "province_id": 1,
        "district_id": 1,
        "commune_id": 1,
        "village_id": 1
    }

@pytest.fixture
def test_property_data() -> Dict[str, Any]:
    """Test property data for creating properties."""
    return {
        "title": "Test Property",
        "description": "A test property for testing purposes",
        "property_type": "house",
        "address": "123 Test Street",
        "province_id": 1,
        "district_id": 1,
        "commune_id": 1,
        "village_id": 1,
        "area": "150.50",
        "price": "250000.00",
        "currency": "USD",
        "bedrooms": 3,
        "bathrooms": 2,
        "floors": 2,
        "year_built": 2020,
        "condition": "new"
    }

# Database setup fixtures
@pytest.fixture
def setup_test_data(db_session):
    """Setup test data in the database."""
    # Create test provinces
    province = Province(name="Test Province", code="TP")
    db_session.add(province)
    
    # Create test districts
    district = District(name="Test District", code="TD", province_id=1)
    db_session.add(district)
    
    # Create test communes
    commune = Commune(name="Test Commune", code="TC", district_id=1)
    db_session.add(commune)
    
    # Create test villages
    village = Village(name="Test Village", code="TV", commune_id=1)
    db_session.add(village)
    
    # Create test branches
    branch = Branch(name="Test Branch", code="TB", address="Test Address")
    db_session.add(branch)
    
    # Create test loan types
    loan_type = LoanType(name="Test Loan", code="TL", description="Test loan type")
    db_session.add(loan_type)
    
    # Create test request types
    request_type = RequestType(name="Test Request", code="TR", description="Test request type")
    db_session.add(request_type)
    
    # Create test permissions
    permissions = [
        Permission(name="user:read", description="Read user information"),
        Permission(name="user:create", description="Create users"),
        Permission(name="user:update", description="Update users"),
        Permission(name="user:delete", description="Delete users"),
        Permission(name="customer:read", description="Read customer information"),
        Permission(name="customer:create", description="Create customers"),
        Permission(name="customer:update", description="Update customers"),
        Permission(name="customer:delete", description="Delete customers"),
        Permission(name="property:read", description="Read property information"),
        Permission(name="property:create", description="Create properties"),
        Permission(name="property:update", description="Update properties"),
        Permission(name="property:delete", description="Delete properties"),
    ]
    
    for permission in permissions:
        db_session.add(permission)
    
    # Create test roles
    roles = [
        Role(name="admin", description="Administrator role"),
        Role(name="user", description="Regular user role"),
        Role(name="manager", description="Manager role"),
    ]
    
    for role in roles:
        db_session.add(role)
    
    db_session.commit()
    
    # Create role-permission mappings
    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    user_role = db_session.query(Role).filter(Role.name == "user").first()
    manager_role = db_session.query(Role).filter(Role.name == "manager").first()
    
    all_permissions = db_session.query(Permission).all()
    read_permissions = db_session.query(Permission).filter(Permission.name.contains(":read")).all()
    create_permissions = db_session.query(Permission).filter(Permission.name.contains(":create")).all()
    
    # Admin gets all permissions
    for permission in all_permissions:
        role_permission = RolePermission(role_id=admin_role.id, permission_id=permission.id)
        db_session.add(role_permission)
    
    # User gets read permissions
    for permission in read_permissions:
        role_permission = RolePermission(role_id=user_role.id, permission_id=permission.id)
        db_session.add(role_permission)
    
    # Manager gets read and create permissions
    for permission in read_permissions + create_permissions:
        role_permission = RolePermission(role_id=manager_role.id, permission_id=permission.id)
        db_session.add(role_permission)
    
    db_session.commit()

@pytest.fixture
def test_user(db_session, test_user_data, setup_test_data):
    """Create a test user with admin role."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(test_user_data["password"])
    
    user = User(
        email=test_user_data["email"],
        password_hash=hashed_password,
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        phone=test_user_data["phone"],
        is_active=test_user_data["is_active"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Assign admin role
    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db_session.add(user_role)
    db_session.commit()
    
    return user

@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authentication headers for authenticated requests."""
    response = client.post("/api/v1/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        return {}

# Utility fixtures
@pytest.fixture
def sample_customers(db_session, setup_test_data):
    """Create sample customers for testing."""
    customers = []
    for i in range(5):
        customer = Customer(
            first_name=f"Customer{i}",
            last_name=f"Test{i}",
            email=f"customer{i}@test.com",
            phone=f"123456789{i}",
            national_id=f"12345678{i}",
            address=f"{i} Test Street",
            province_id=1,
            district_id=1,
            commune_id=1,
            village_id=1
        )
        db_session.add(customer)
        customers.append(customer)
    
    db_session.commit()
    return customers

@pytest.fixture
def sample_properties(db_session, setup_test_data, test_user):
    """Create sample properties for testing."""
    properties = []
    for i in range(3):
        property_obj = Property(
            title=f"Test Property {i}",
            description=f"Test property description {i}",
            property_type="house",
            address=f"{i} Test Street",
            province_id=1,
            district_id=1,
            commune_id=1,
            village_id=1,
            area=100.0 + i * 50,
            price=200000.0 + i * 50000,
            currency="USD",
            bedrooms=2 + i,
            bathrooms=1 + i,
            floors=1,
            year_built=2020,
            condition="good",
            owner_id=test_user.id
        )
        db_session.add(property_obj)
        properties.append(property_obj)
    
    db_session.commit()
    return properties 