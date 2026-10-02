from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import PolicyPurchase, User, Policy, Claim
from schemas import (
    PurchaseDetailOut,
    PurchaseListResponse,
    PurchaseCustomerOut,
    PurchasePolicyOut,
    PurchaseAgentOut
)
from dependencies import require_admin

router = APIRouter(prefix="/api/admin/policy-purchases", tags=["Admin Policy Purchases"])

def format_purchase_detail(p: PolicyPurchase, db: Session) -> PurchaseDetailOut:
    customer_data = None
    if p.customer:
        customer_data = PurchaseCustomerOut(
            id=p.customer.id,
            full_name=p.customer.full_name,
            email=p.customer.email,
            phone=p.customer.phone
        )

    policy_data = None
    if p.policy:
        policy_data = PurchasePolicyOut(
            id=p.policy.id,
            policy_number=p.policy.policy_number,
            name=p.policy.name,
            type=p.policy.type,
            premium=p.policy.premium,
            duration_months=p.policy.duration_months
        )

    agent_data = None
    if p.agent:
        agent_data = PurchaseAgentOut(
            id=p.agent.id,
            full_name=p.agent.full_name,
            email=p.agent.email
        )

    claims_count = db.query(Claim).filter(Claim.policy_purchase_id == p.id).count()

    return PurchaseDetailOut(
        id=p.id,
        policy_id=p.policy_id,
        customer_id=p.customer_id,
        agent_id=p.agent_id,
        start_date=p.start_date,
        end_date=p.end_date,
        status=p.status,
        created_at=p.created_at,
        customer=customer_data,
        policy=policy_data,
        agent=agent_data,
        claims_count=claims_count
    )

@router.get("", response_model=PurchaseListResponse)
def list_policy_purchases(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(PolicyPurchase).join(PolicyPurchase.customer).join(PolicyPurchase.policy)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                Policy.policy_number.ilike(search_term),
                Policy.name.ilike(search_term)
            )
        )

    if status and status.upper() in ["ACTIVE", "EXPIRED", "CANCELLED"]:
        query = query.filter(PolicyPurchase.status == status.upper())

    total = query.count()
    purchases = query.order_by(PolicyPurchase.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [format_purchase_detail(p, db) for p in purchases]

    return PurchaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=PurchaseDetailOut)
def get_policy_purchase_by_id(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    purchase = db.query(PolicyPurchase).filter(PolicyPurchase.id == id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Policy purchase not found")
    return format_purchase_detail(purchase, db)
