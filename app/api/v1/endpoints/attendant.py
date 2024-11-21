from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_admin, get_password_hash, verify_password, create_access_token
from app.models import models
from app.schemas import schemas
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    """
    Authenticate attendant and generate access token.

    Parameters:
    - **email**: Attendant's email address
    - **passcode**: Attendant's passcode

    Returns:
    - **access_token**: JWT token for authentication
    - **token_type**: Token type (bearer)
    - **attendant_id**: UUID of authenticated attendant

    The access token will contain the attendant's branch information
    for branch-specific operations.
    """
    body = await request.json()
    email = body.get("email")
    passcode = body.get("passcode")
    
    if not email or not passcode:
        raise HTTPException(status_code=400, detail="Email and passcode required")
    
    attendant = db.query(models.Attendant).filter(models.Attendant.email == email).first()
    if not attendant or not verify_password(passcode, attendant.passcode):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={
        "sub": attendant.email,
        "attendant_id": str(attendant.id),
        "branch_id": str(attendant.branch_id),
        "role": "attendant"
    })
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "attendant_id": str(attendant.id)
    }

@router.get("/", response_model=List[schemas.Attendant])
async def get_attendants(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    attendants = db.query(models.Attendant).all()
    return attendants

@router.post("/create", response_model=schemas.Attendant)
async def create_attendant(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new attendant account.

    Parameters:
    - **email**: Attendant's email address
    - **passcode**: Attendant's passcode
    - **branch_id**: UUID of the branch where attendant works

    Returns:
    - Created attendant object (without passcode)

    Requirements:
    * Must be authenticated as admin
    * Email must be unique
    * Branch must exist
    * All fields are required
    """
    body = await request.json()
    email = body.get("email")
    passcode = body.get("passcode")
    branch_id = body.get("branch_id")
    
    if not all([email, passcode, branch_id]):
        raise HTTPException(status_code=400, detail="Email, passcode, and branch_id required")
    
    try:
        branch_uuid = UUID(branch_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid branch ID format")
    
    # Check if attendant already exists
    if db.query(models.Attendant).filter(models.Attendant.email == email).first():
        raise HTTPException(status_code=400, detail="Attendant with this email already exists")
    
    # Check if branch exists
    branch = db.query(models.Branch).filter(models.Branch.id == branch_uuid).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
        
    db_attendant = models.Attendant(
        email=email,
        passcode=get_password_hash(passcode),
        branch_id=branch_uuid,
        created_by=current_admin.id
    )
    db.add(db_attendant)
    db.commit()
    db.refresh(db_attendant)
    return db_attendant

@router.get("/{attendant_id}", response_model=schemas.Attendant)
async def get_attendant(
    attendant_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    attendant = db.query(models.Attendant).filter(models.Attendant.id == attendant_id).first()
    if not attendant:
        raise HTTPException(status_code=404, detail="Attendant not found")
    return attendant

@router.get("/branch/{branch_id}", response_model=List[schemas.Attendant])
async def get_attendants_by_branch(
    branch_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    List all attendants assigned to a specific branch.

    Parameters:
    - **branch_id**: UUID of the branch

    Returns:
    - List of attendant objects assigned to the branch

    Requires admin authentication.
    """
    attendants = db.query(models.Attendant).filter(models.Attendant.branch_id == branch_id).all()
    return attendants