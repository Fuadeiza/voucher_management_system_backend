from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import models
from app.schemas import schemas
from typing import List
from uuid import UUID
import random
import string
from datetime import datetime

router = APIRouter()

def generate_voucher_code(company_acronym: str, length: int = 6) -> str:
    """Generate a unique voucher code"""
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(length))
    return f"{company_acronym}-{random_str}"

@router.post("/create", response_model=schemas.Voucher)
async def create_voucher(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new voucher for a company.

    Parameters:
    - **company_id**: UUID of the company for which to create the voucher
    
    Returns:
    - **Voucher**: Created voucher object with auto-generated code
    
    The voucher code will be automatically generated using the company's acronym
    and a random string, e.g., "FB-12ABC4"
    
    Requirements:
    * Must be authenticated as admin
    * Company must exist
    * Company acronym must be set
    """
    body = await request.json()
    company_id = body.get("company_id") 
    try:
        company_uuid = UUID(company_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid company ID format")
    
    # Check if company exists
    company = db.query(models.Company).filter(models.Company.id == company_uuid).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Generate unique voucher code
    code = generate_voucher_code(company.acronym)
    while db.query(models.Voucher).filter(models.Voucher.code == code).first():
        code = generate_voucher_code(company.acronym)
        
    db_voucher = models.Voucher(
        code=code,
        company_id=company_uuid,
        created_by=current_admin.id
    )
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    return db_voucher

@router.get("/", response_model=List[schemas.Voucher])
async def get_vouchers(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    vouchers = db.query(models.Voucher).all()
    return vouchers

@router.get("/{voucher_id}", response_model=schemas.Voucher)
async def get_voucher(
    voucher_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    voucher = db.query(models.Voucher).filter(models.Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher

@router.post("/verify/{code}")
async def verify_voucher(
    code: str,
    db: Session = Depends(get_db)
):
    """
    Verify a voucher's status without using it.

    Parameters:
    - **code**: The voucher code to verify
    
    Returns:
    - **status**: Current status of the voucher (active/used/invalid)
    - **company**: Name of the company that issued the voucher
    - **created_at**: When the voucher was created
    - **used_at**: When the voucher was used (if applicable)
    
    This endpoint can be used to check if a voucher is valid
    before attempting to use it.
    """
    voucher = db.query(models.Voucher).filter(models.Voucher.code == code.upper()).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    return {
        "status": voucher.status,
        "company": voucher.company.name,
        "created_at": voucher.created_at,
        "used_at": voucher.used_at
    }

@router.post("/use/{code}")
async def use_voucher(
    code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    body = await request.json()
    attendant_id = body.get("attendant_id")
    
    try:
        attendant_uuid = UUID(attendant_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid attendant ID format")
    
    # Verify attendant exists
    attendant = db.query(models.Attendant).filter(models.Attendant.id == attendant_uuid).first()
    if not attendant:
        raise HTTPException(status_code=404, detail="Attendant not found")
    
    voucher = db.query(models.Voucher).filter(models.Voucher.code == code.upper()).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    if voucher.status != "active":
        raise HTTPException(status_code=400, detail=f"Voucher is {voucher.status}")
    
    voucher.status = "used"
    voucher.used_by = attendant_uuid
    voucher.used_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Voucher used successfully",
        "voucher_code": voucher.code,
        "used_by": attendant.email,
        "branch": attendant.branch.name
    }

@router.post("/invalidate/{code}")
async def invalidate_voucher(
    code: str,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    voucher = db.query(models.Voucher).filter(models.Voucher.code == code.upper()).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    if voucher.status == "invalid":
        raise HTTPException(status_code=400, detail="Voucher is already invalidated")
    
    voucher.status = "invalid"
    db.commit()
    
    return {"message": "Voucher invalidated successfully"}

@router.post("/revert/{code}")
async def revert_voucher_usage(
    code: str,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    voucher = db.query(models.Voucher).filter(models.Voucher.code == code.upper()).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    if voucher.status != "used":
        raise HTTPException(status_code=400, detail="Can only revert used vouchers")
    
    voucher.status = "active"
    voucher.used_by = None
    voucher.used_at = None
    db.commit()
    
    return {"message": "Voucher usage reverted successfully"}

@router.get("/company/{company_id}/stats")
async def get_company_voucher_stats(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    # Verify company exists
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    total = db.query(models.Voucher).filter(
        models.Voucher.company_id == company_id
    ).count()
    
    active = db.query(models.Voucher).filter(
        models.Voucher.company_id == company_id,
        models.Voucher.status == "active"
    ).count()
    
    used = db.query(models.Voucher).filter(
        models.Voucher.company_id == company_id,
        models.Voucher.status == "used"
    ).count()
    
    invalid = db.query(models.Voucher).filter(
        models.Voucher.company_id == company_id,
        models.Voucher.status == "invalid"
    ).count()
    
    return {
        "company_name": company.name,
        "total_vouchers": total,
        "active_vouchers": active,
        "used_vouchers": used,
        "invalid_vouchers": invalid,
        "usage_percentage": (used/total * 100) if total > 0 else 0
    }