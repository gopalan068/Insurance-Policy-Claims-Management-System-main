from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, PolicyPurchase, Claim, Policy
from dependencies import require_agent

router = APIRouter(prefix="/api/agent/purchases", tags=["Agent Purchases"])


@router.get("")
def get_assigned_purchases(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    query = db.query(PolicyPurchase).filter(PolicyPurchase.agent_id == aid)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.join(Policy).join(User).filter(
            or_(
                Policy.policy_number.ilike(search_term),
                Policy.name.ilike(search_term),
                User.full_name.ilike(search_term),
            )
        )

    if status and status.upper() in ["ACTIVE", "EXPIRED", "CANCELLED"]:
        query = query.filter(PolicyPurchase.status == status.upper())

    total = query.count()
    purchases = query.order_by(PolicyPurchase.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for p in purchases:
        pol = p.policy
        cust = p.customer
        claims_count = db.query(Claim).filter(Claim.policy_purchase_id == p.id).count()
        items.append({
            "id": p.id,
            "policy_number": pol.policy_number if pol else "N/A",
            "policy_name": pol.name if pol else "N/A",
            "policy_type": pol.type if pol else "N/A",
            "premium": pol.premium if pol else 0,
            "customer_name": cust.full_name if cust else "N/A",
            "customer_email": cust.email if cust else "N/A",
            "start_date": p.start_date,
            "end_date": p.end_date,
            "status": p.status,
            "claims_count": claims_count,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{purchase_id}")
def get_purchase_detail(
    purchase_id: int,
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    purchase = db.query(PolicyPurchase).filter(PolicyPurchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    # Verify ownership
    if purchase.agent_id != aid:
        raise HTTPException(status_code=403, detail="Access denied: This purchase is not assigned to you")

    pol = purchase.policy
    cust = purchase.customer
    claims = db.query(Claim).filter(Claim.policy_purchase_id == purchase.id).all()

    return {
        "id": purchase.id,
        "policy": {
            "id": pol.id if pol else None,
            "policy_number": pol.policy_number if pol else "N/A",
            "name": pol.name if pol else "N/A",
            "type": pol.type if pol else "N/A",
            "premium": pol.premium if pol else 0,
            "duration_months": pol.duration_months if pol else 0,
        },
        "customer": {
            "id": cust.id if cust else None,
            "full_name": cust.full_name if cust else "N/A",
            "email": cust.email if cust else "N/A",
            "phone": cust.phone if cust else None,
        },
        "start_date": purchase.start_date,
        "end_date": purchase.end_date,
        "status": purchase.status,
        "claims": [{
            "id": c.id,
            "claim_number": c.claim_number,
            "amount": c.amount,
            "reason": c.reason,
            "status": c.status,
            "claim_date": c.claim_date,
        } for c in claims],
    }
