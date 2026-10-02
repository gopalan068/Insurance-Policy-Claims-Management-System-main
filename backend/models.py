from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from database import Base

def utc_now():
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    AGENT = "AGENT"
    CLAIMS_OFFICER = "CLAIMS_OFFICER"

class PolicyType(str, enum.Enum):
    HEALTH = "HEALTH"
    LIFE = "LIFE"
    VEHICLE = "VEHICLE"
    TRAVEL = "TRAVEL"
    HOME = "HOME"

class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class PurchaseStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class ClaimStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="CUSTOMER", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    customer_purchases = relationship(
        "PolicyPurchase",
        back_populates="customer",
        foreign_keys="[PolicyPurchase.customer_id]",
        cascade="all, delete-orphan"
    )
    agent_purchases = relationship(
        "PolicyPurchase",
        back_populates="agent",
        foreign_keys="[PolicyPurchase.agent_id]"
    )
    claims = relationship(
        "Claim",
        back_populates="customer",
        cascade="all, delete-orphan"
    )
    reviews_done = relationship(
        "ClaimReview",
        back_populates="officer"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="admin"
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    type = Column(String(30), nullable=False)  # HEALTH, LIFE, etc.
    description = Column(Text, nullable=True)
    premium = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, INACTIVE
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    purchases = relationship("PolicyPurchase", back_populates="policy", cascade="all, delete-orphan")


class PolicyPurchase(Base):
    __tablename__ = "policy_purchases"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, EXPIRED, CANCELLED
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    policy = relationship("Policy", back_populates="purchases")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="customer_purchases")
    agent = relationship("User", foreign_keys=[agent_id], back_populates="agent_purchases")
    claims = relationship("Claim", back_populates="policy_purchase", cascade="all, delete-orphan")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(50), unique=True, index=True, nullable=False)
    policy_purchase_id = Column(Integer, ForeignKey("policy_purchases.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    claim_date = Column(DateTime, default=utc_now, nullable=False)
    status = Column(String(30), default="SUBMITTED", nullable=False)  # SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    policy_purchase = relationship("PolicyPurchase", back_populates="claims")
    customer = relationship("User", back_populates="claims")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    reviews = relationship("ClaimReview", back_populates="claim", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    uploaded_date = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    claim = relationship("Claim", back_populates="documents")


class ClaimReview(Base):
    __tablename__ = "claim_reviews"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    officer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    decision = Column(String(30), nullable=False)  # APPROVED, REJECTED, UNDER_REVIEW
    remarks = Column(Text, nullable=False)
    review_date = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    claim = relationship("Claim", back_populates="reviews")
    officer = relationship("User", back_populates="reviews_done")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., CREATE_USER, DEACTIVATE_USER, etc.
    target_type = Column(String(50), nullable=False)  # USER, POLICY, etc.
    target_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    admin = relationship("User", back_populates="audit_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(30), default="INFO", nullable=False)  # INFO, SUCCESS, WARNING, ERROR
    is_read = Column(Boolean, default=False, nullable=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")

