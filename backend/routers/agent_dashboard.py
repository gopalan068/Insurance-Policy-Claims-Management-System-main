from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Policy, PolicyPurchase, Claim, Document
from dependencies import require_agent

router = APIRouter(prefix="/api/agent/dashboard", tags=["Agent Dashboard"])


@router.get("")
def get_agent_dashboard(
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    # Assigned purchases
    assigned_purchases = db.query(PolicyPurchase).filter(PolicyPurchase.agent_id == aid).all()
    active_purchases = [p for p in assigned_purchases if p.status == "ACTIVE"]
    expired_purchases = [p for p in assigned_purchases if p.status == "EXPIRED"]

    # Assigned customers (unique)
    customer_ids = set(p.customer_id for p in assigned_purchases)
    total_customers = len(customer_ids)

    # Claims related to assigned purchases
    purchase_ids = [p.id for p in assigned_purchases]
    claims = db.query(Claim).filter(Claim.policy_purchase_id.in_(purchase_ids)).all() if purchase_ids else []
    pending_claims = [c for c in claims if c.status in ["SUBMITTED", "UNDER_REVIEW"]]
    approved_claims = [c for c in claims if c.status == "APPROVED"]

    # Expiring soon (within 30 days)
    now = datetime.now(timezone.utc)
    expiring_soon = [p for p in active_purchases if p.end_date and (p.end_date - now).days <= 30]

    # Purchases by status for chart
    purchases_by_status = {
        "ACTIVE": len(active_purchases),
        "EXPIRED": len(expired_purchases),
        "CANCELLED": len([p for p in assigned_purchases if p.status == "CANCELLED"]),
    }

    # Claims by status for chart
    claims_by_status = {
        "SUBMITTED": len([c for c in claims if c.status == "SUBMITTED"]),
        "UNDER_REVIEW": len([c for c in claims if c.status == "UNDER_REVIEW"]),
        "APPROVED": len(approved_claims),
        "REJECTED": len([c for c in claims if c.status == "REJECTED"]),
    }

    # Recent purchases
    recent_purchases = sorted(assigned_purchases, key=lambda x: x.created_at, reverse=True)[:5]
    recent_purchases_out = []
    for p in recent_purchases:
        pol = p.policy
        cust = p.customer
        recent_purchases_out.append({
            "id": p.id,
            "policy_number": pol.policy_number if pol else "N/A",
            "policy_name": pol.name if pol else "N/A",
            "policy_type": pol.type if pol else "N/A",
            "customer_name": cust.full_name if cust else "N/A",
            "premium": pol.premium if pol else 0,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "status": p.status,
        })

    return {
        "agent_name": agent.full_name,
        "total_customers": total_customers,
        "total_purchases": len(assigned_purchases),
        "active_purchases": len(active_purchases),
        "expired_purchases": len(expired_purchases),
        "expiring_soon": len(expiring_soon),
        "total_claims": len(claims),
        "pending_claims": len(pending_claims),
        "approved_claims": len(approved_claims),
        "purchases_by_status": purchases_by_status,
        "claims_by_status": claims_by_status,
        "recent_purchases": recent_purchases_out,
    }
