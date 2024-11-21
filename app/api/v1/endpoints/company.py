from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import models
from app.schemas import schemas
from typing import List
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[schemas.Company])
async def get_companies(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    List all companies in the system.

    Returns:
    - List of company objects including:
        - company ID
        - name
        - acronym
        - creation timestamp

    Requires admin authentication.
    """
    try:
        # Add debug logging
        print(f"Getting companies for admin: {current_admin.email}")
        companies = db.query(models.Company).all()
        return companies
    except Exception as e:
        print(f"Error getting companies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", response_model=schemas.Company)
async def create_company(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Create a new company.

    Parameters:
    - **name**: Company full name
    - **acronym**: Company acronym (used for voucher code generation)

    Returns:
    - Created company object

    The acronym:
    * Must be unique
    * Will be automatically converted to uppercase
    * Will be used in voucher code generation (e.g., "FB-123ABC")

    Requires admin authentication.
    """

    try:
        body = await request.json()
        print(f"Creating company with data: {body}")  

        name = body.get("name")
        acronym = body.get("acronym")
        
        if not name or not acronym:
            raise HTTPException(status_code=400, detail="Name and acronym required")
        
        # Check if company with acronym already exists
        db_company = db.query(models.Company).filter(models.Company.acronym == acronym.upper()).first()
        if db_company:
            raise HTTPException(status_code=400, detail="Company with this acronym already exists")
            
        db_company = models.Company(
            name=name,
            acronym=acronym.upper()
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except Exception as e:
        print(f"Error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{company_id}", response_model=schemas.Company)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    """
    Get voucher statistics for a specific company.

    Parameters:
    - **company_id**: UUID of the company

    Returns:
    - **company_name**: Name of the company
    - **total_vouchers**: Total number of vouchers created
    - **active_vouchers**: Number of unused vouchers
    - **used_vouchers**: Number of used vouchers
    - **invalid_vouchers**: Number of invalidated vouchers
    - **usage_percentage**: Percentage of vouchers used

    Requires admin authentication.
    """
    # Check if company exists
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    total_vouchers = db.query(models.Voucher).filter(
        models.Voucher.company_id == company_id
    ).count()
    
    used_vouchers = db.query(models.Voucher).filter(
        models.Voucher.company_id == company_id,
        models.Voucher.status == "used"
    ).count()
    
    return {
        "company_name": company.name,
        "company_acronym": company.acronym,
        "total_vouchers": total_vouchers,
        "used_vouchers": used_vouchers,
        "usage_percentage": (used_vouchers / total_vouchers * 100) if total_vouchers > 0 else 0
    }

@router.put("/{company_id}", response_model=schemas.Company)
async def update_company(
    company_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    body = await request.json()
    name = body.get("name")
    acronym = body.get("acronym")
    
    if name:
        company.name = name
    if acronym:
        # Check if new acronym already exists
        existing = db.query(models.Company).filter(
            models.Company.acronym == acronym.upper(),
            models.Company.id != company_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Company with this acronym already exists")
        company.acronym = acronym.upper()
    
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}/vouchers", response_model=List[schemas.Voucher])
async def get_company_vouchers(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    try:
        # Debug logging
        print(f"Fetching vouchers for company: {company_id}")
        
        # Verify company exists
        company = db.query(models.Company).filter(models.Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get vouchers with debug logging
        vouchers = db.query(models.Voucher).filter(
            models.Voucher.company_id == company_id
        ).order_by(models.Voucher.created_at.desc()).all()
        
        print(f"Found {len(vouchers)} vouchers")
        return vouchers
        
    except Exception as e:
        print(f"Error fetching vouchers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))