from fastapi import FastAPI
from app.api.v1.endpoints import admin, attendant, voucher, company, branch
from app.core.config import settings
from app.core.database import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voucher Management System",
    description="""
    A system for managing company vouchers with the following features:
    
    * 👤 Admin Management
    * 🏢 Company Management
    * 🏪 Branch Management
    * 👥 Attendant Management
    * 🎫 Voucher Creation and Management
    
    ## Roles
    
    * **Admin**: Can create and manage everything
    * **Attendant**: Can verify and use vouchers
    
    ## Authentication
    
    All endpoints require authentication except login endpoints.
    Use the Bearer token received after login.
    """,
    version="1.0.0",
    contact={
        "name": "Garba Fuad",
        "email": "garbafuad@gmail.com",
    },
    license_info={
        "name": "Private",
    },
)

# Tags metadata for better documentation organization
tags_metadata = [
    {
        "name": "admin",
        "description": "Operations with admin accounts. Only admins can access these endpoints.",
    },
    {
        "name": "company",
        "description": "Company management operations. Required for voucher creation.",
    },
    {
        "name": "branch",
        "description": "Branch management operations. Required for attendant assignment.",
    },
    {
        "name": "attendant",
        "description": "Attendant management and authentication operations.",
    },
    {
        "name": "voucher",
        "description": "Voucher creation, verification, and usage operations.",
    },
]

app.openapi_tags = tags_metadata

# Include routers
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(company.router, prefix="/api/v1/company", tags=["company"])
app.include_router(branch.router, prefix="/api/v1/branch", tags=["branch"])
app.include_router(attendant.router, prefix="/api/v1/attendant", tags=["attendant"])
app.include_router(voucher.router, prefix="/api/v1/voucher", tags=["voucher"])

@app.get("/", tags=["root"])
async def root():
    """
    Welcome endpoint with system information.
    """
    return {
        "message": "Welcome to Voucher Management System",
        "version": "1.0.0",
        "docs": "/docs or /redoc",
        "status": "operational"
    }