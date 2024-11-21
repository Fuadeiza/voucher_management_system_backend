from sqlalchemy import Column, String, ForeignKey, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class Branch(Base):
    __tablename__ = "branch"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    attendants = relationship("Attendant", back_populates="branch")

class Admin(Base):
    __tablename__ = "admin"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    passcode = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Company(Base):
    __tablename__ = "company"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    acronym = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    vouchers = relationship("Voucher", back_populates="company")

class Attendant(Base):
    __tablename__ = "attendant"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    passcode = Column(String(255), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branch.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("admin.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    branch = relationship("Branch", back_populates="attendants")
    vouchers = relationship("Voucher", back_populates="attendant")

class Voucher(Base):
    __tablename__ = "voucher"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=False)
    status = Column(Text, default='active')
    used_by = Column(UUID(as_uuid=True), ForeignKey("attendant.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("admin.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    company = relationship("Company", back_populates="vouchers")
    attendant = relationship("Attendant", back_populates="vouchers")