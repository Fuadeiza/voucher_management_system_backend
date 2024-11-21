from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import models
from app.schemas import schemas
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[schemas.Branch])
async def get_branches(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    List all branches in the system.

    Returns:
    - List of branch objects including:
        - branch ID
        - name
        - location
        - creation timestamp

    Requires admin authentication.
    """
    branches = db.query(models.Branch).all()
    return branches

async def create_branch(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new branch.

    Parameters:
    - **name**: Branch name
    - **location**: Branch location/address

    Returns:
    - Created branch object

    Requirements:
    * Must be authenticated as admin
    * Name and location combination must be unique
    * Both name and location are required
    """
    body = await request.json()
    name = body.get("name")
    location = body.get("location")
    
    if not name or not location:
        raise HTTPException(status_code=400, detail="Name and location required")
    
    # Check if branch with same name and location exists
    existing_branch = db.query(models.Branch).filter(
        models.Branch.name == name,
        models.Branch.location == location
    ).first()
    
    if existing_branch:
        raise HTTPException(
            status_code=400, 
            detail="Branch with this name and location already exists"
        )
        
    db_branch = models.Branch(
        name=name,
        location=location
    )
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@router.get("/{branch_id}", response_model=schemas.Branch)
async def get_branch(
    branch_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Get details of a specific branch.

    Parameters:
    - **branch_id**: UUID of the branch

    Returns:
    - Branch object if found

    Requires admin authentication.
    """
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.put("/{branch_id}", response_model=schemas.Branch)
async def update_branch(
    branch_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    body = await request.json()
    name = body.get("name")
    location = body.get("location")
    
    if name:
        branch.name = name
    if location:
        branch.location = location
        
    db.commit()
    db.refresh(branch)
    return branch