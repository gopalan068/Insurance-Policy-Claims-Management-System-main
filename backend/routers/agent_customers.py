from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, PolicyPurchase, Claim, Policy
from dependencies import require_agent

router = APIRouter(prefix="/api/agent/customers", tags=["Agent Customers"])


@router.get("")
def get_assigned_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    # Get unique customers from agent's purchases
    purchases = db.query(PolicyPurchase).filter(PolicyPurchase.agent_id == aid).all()
    customer_ids = list(set(p.customer_id for p in purchases))

    if not customer_ids:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    query = db.query(User).filter(User.id.in_(customer_ids))

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(User.full_name.ilike(search_term), User.email.ilike(search_term))
        )

    total = query.count()
    customers = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for c in customers:
        cust_purchases = [p for p in purchases if p.customer_id == c.id]
        active_count = len([p for p in cust_purchases if p.status == "ACTIVE"])
        purchase_ids = [p.id for p in cust_purchases]
        claims_count = db.query(Claim).filter(Claim.policy_purchase_id.in_(purchase_ids)).count() if purchase_ids else 0

        items.append({
            "id": c.id,
            "full_name": c.full_name,
            "email": c.email,
            "phone": c.phone,
            "is_active": c.is_active,
            "policies_count": len(cust_purchases),
            "active_policies": active_count,
            "claims_count": claims_count,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{customer_id}")
def get_customer_detail(
    customer_id: int,
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    # Verify customer belongs to this agent
    customer = db.query(User).filter(User.id == customer_id, User.role == "CUSTOMER").first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify assignment
    assignment = db.query(PolicyPurchase).filter(
        PolicyPurchase.customer_id == customer_id,
        PolicyPurchase.agent_id == aid
    ).first()
    if not assignment:
        raise HTTPException(status_code=403, detail="Access denied: This customer is not assigned to you")

    # Get all purchases for this customer assigned to this agent
    purchases = db.query(PolicyPurchase).filter(
        PolicyPurchase.customer_id == customer_id,
        PolicyPurchase.agent_id == aid
    ).all()

    purchases_out = []
    for p in purchases:
        pol = p.policy
        claims = db.query(Claim).filter(Claim.policy_purchase_id == p.id).all()
        purchases_out.append({
            "id": p.id,
            "policy_number": pol.policy_number if pol else "N/A",
            "policy_name": pol.name if pol else "N/A",
            "policy_type": pol.type if pol else "N/A",
            "premium": pol.premium if pol else 0,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "status": p.status,
            "claims": [{
                "id": c.id,
                "claim_number": c.claim_number,
                "amount": c.amount,
                "reason": c.reason,
                "status": c.status,
                "claim_date": c.claim_date,
            } for c in claims],
        })

    return {
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "phone": customer.phone,
            "is_active": customer.is_active,
            "created_at": customer.created_at,
        },
        "purchases": purchases_out,
    }
