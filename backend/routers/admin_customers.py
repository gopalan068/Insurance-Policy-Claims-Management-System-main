from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, PolicyPurchase, Claim, Policy
from schemas import CustomerDetailOut, CustomerListResponse
from dependencies import require_admin

router = APIRouter(prefix="/api/admin/customers", tags=["Admin Customers"])

def format_customer_detail(c: User, db: Session, include_relations: bool = False) -> CustomerDetailOut:
    purchases = db.query(PolicyPurchase).filter(PolicyPurchase.customer_id == c.id).all()
    claims = db.query(Claim).filter(Claim.customer_id == c.id).all()

    policies_list = []
    if include_relations:
        for pur in purchases:
            policies_list.append({
                "purchase_id": pur.id,
                "policy_id": pur.policy_id,
                "policy_number": pur.policy.policy_number if pur.policy else "N/A",
                "policy_name": pur.policy.name if pur.policy else "N/A",
                "type": pur.policy.type if pur.policy else "N/A",
                "premium": pur.policy.premium if pur.policy else 0.0,
                "start_date": pur.start_date,
                "end_date": pur.end_date,
                "status": pur.status,
                "agent_name": pur.agent.full_name if pur.agent else "Direct Purchase"
            })

    claims_list = []
    if include_relations:
        for clm in claims:
            claims_list.append({
                "claim_id": clm.id,
                "claim_number": clm.claim_number,
                "reason": clm.reason,
                "amount": clm.amount,
                "claim_date": clm.claim_date,
                "status": clm.status
            })

    return CustomerDetailOut(
        id=c.id,
        full_name=c.full_name,
        email=c.email,
        phone=c.phone,
        role=c.role,
        is_active=c.is_active,
        created_at=c.created_at,
        policies_count=len(purchases),
        claims_count=len(claims),
        policies=policies_list,
        claims=claims_list
    )

@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(User).filter(User.role == "CUSTOMER")

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.phone.ilike(search_term)
            )
        )

    if status is not None and status != "":
        if status.lower() in ["active", "true", "1"]:
            query = query.filter(User.is_active == True)
        elif status.lower() in ["inactive", "false", "0"]:
            query = query.filter(User.is_active == False)

    total = query.count()
    customers = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [format_customer_detail(c, db, include_relations=False) for c in customers]

    return CustomerListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=CustomerDetailOut)
def get_customer_details(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    customer = db.query(User).filter(User.id == id, User.role == "CUSTOMER").first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return format_customer_detail(customer, db, include_relations=True)
