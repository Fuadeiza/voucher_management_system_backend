from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, get_current_admin, get_password_hash, verify_password
from app.models import models
from app.schemas import schemas
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("/login", status_code=200)
async def login(request: Request, db: Session = Depends(get_db)):
    """
    Authenticate admin user and generate access token.

    Parameters:
    - **email**: Admin's email address
    - **passcode**: Admin's passcode

    Returns:
    - **access_token**: JWT token for authentication
    - **token_type**: Token type (bearer)
    - **admin_id**: UUID of authenticated admin

    Use the returned access token in the Authorization header for protected endpoints:
    `Authorization: Bearer <token>`
    """
    try:
        body = await request.json()
        email = body.get("email")
        passcode = body.get("passcode")
        
        print(f"Login attempt for: {email}")  # Debug log
        
        admin = db.query(models.Admin).filter(models.Admin.email == email).first()
        if not admin or not verify_password(passcode, admin.passcode):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": admin.email})
        print(f"Generated token for {email}: {access_token}")  # Debug log
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create", response_model=schemas.Admin)
async def create_admin(request: Request, db: Session = Depends(get_db)):
    """
    Create a new admin account.

    Parameters:
    - **email**: New admin's email address
    - **passcode**: New admin's passcode

    Returns:
    - Created admin object (without passcode)

    The passcode will be automatically hashed before storage.
    Email must be unique in the system.
    """
    body = await request.json()
    email = body.get("email")
    passcode = body.get("passcode")
    
    if not email or not passcode:
        raise HTTPException(status_code=400, detail="Email and passcode required")
    
    # Check if admin already exists
    if db.query(models.Admin).filter(models.Admin.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    db_admin = models.Admin(
        email=email,
        passcode=get_password_hash(passcode)
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.get("/", response_model=List[schemas.Admin])
async def get_admins(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    List all admin accounts.

    Returns:
    - List of admin objects (without passcodes)

    Requires admin authentication.
    """
    admins = db.query(models.Admin).all()
    return admins

@router.get("/{admin_id}", response_model=schemas.Admin)
async def get_admin(
    admin_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin