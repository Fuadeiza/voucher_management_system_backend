from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class VoucherStatus(str, Enum):
    active = "active"
    used = "used"
    invalid = "invalid"

# Base schemas
class BranchBase(BaseModel):
    name: str
    location: str

class AdminBase(BaseModel):
    email: EmailStr

class CompanyBase(BaseModel):
    name: str
    acronym: str

class AttendantBase(BaseModel):
    email: EmailStr
    branch_id: UUID

class VoucherBase(BaseModel):
    company_id: UUID

# Create schemas
class BranchCreate(BranchBase):
    pass

class AdminCreate(AdminBase):
    passcode: str

class CompanyCreate(CompanyBase):
    pass

class AttendantCreate(AttendantBase):
    passcode: str

class VoucherCreate(VoucherBase):
    pass

# Read schemas
class Branch(BranchBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class Admin(AdminBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class Company(CompanyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class Attendant(AttendantBase):
    id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class Voucher(VoucherBase):
    id: UUID
    code: str
    status: VoucherStatus
    used_by: Optional[UUID]
    used_at: Optional[datetime]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True