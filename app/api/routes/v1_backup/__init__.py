# API v1 routes
from app.api.routes.v1.auth import router as auth_router
from app.api.routes.v1.customers import router as customers_router
from app.api.routes.v1.branches import router as branches_router
from app.api.routes.v1.loan_types import router as loan_types_router
from app.api.routes.v1.request_types import router as request_types_router
from app.api.routes.v1.property import router as property_router
from app.api.routes.v1.loan_request import router as loan_request_router
from app.api.routes.v1.collateral import router as collateral_router
from app.api.routes.v1.image import router as image_router
from app.api.routes.v1.rbac import router as rbac_router

# List of all v1 routers
v1_routers = [
    auth_router,
    customers_router,
    branches_router,
    loan_types_router,
    request_types_router,
    property_router,
    loan_request_router,
    collateral_router,
    image_router,
    rbac_router,
] 