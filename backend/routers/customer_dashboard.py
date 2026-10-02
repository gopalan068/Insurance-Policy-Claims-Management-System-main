from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, PolicyPurchase, Claim, Notification, Document
from schemas import (
    CustomerDashboardResponse,
    CustomerPurchaseOut,
    CustomerClaimOut
)
from dependencies import require_customer

router = APIRouter(prefix="/api/customer/dashboard", tags=["Customer Dashboard"])

@router.get("", response_model=CustomerDashboardResponse)
def get_customer_dashboard(
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    cid = current_customer.id

    # Purchases metrics
    all_purchases = db.query(PolicyPurchase).filter(PolicyPurchase.customer_id == cid).all()
    total_policies = len(all_purchases)
    active_policies = sum(1 for p in all_purchases if p.status == "ACTIVE")
    expired_policies = sum(1 for p in all_purchases if p.status == "EXPIRED")

    # Claims metrics
    all_claims = db.query(Claim).filter(Claim.customer_id == cid).all()
    total_claims = len(all_claims)
    pending_claims = sum(1 for c in all_claims if c.status in ["SUBMITTED", "UNDER_REVIEW"])
    approved_claims = sum(1 for c in all_claims if c.status == "APPROVED")
    rejected_claims = sum(1 for c in all_claims if c.status == "REJECTED")

    # Unread notifications
    unread_notifs = db.query(Notification).filter(
        Notification.user_id == cid,
        Notification.is_read == False
    ).count()

    # Recent purchases (last 5)
    recent_purchases_raw = db.query(PolicyPurchase).filter(
        PolicyPurchase.customer_id == cid
    ).order_by(PolicyPurchase.id.desc()).limit(5).all()

    recent_purchases = []
    for p in recent_purchases_raw:
        claims_count = db.query(Claim).filter(Claim.policy_purchase_id == p.id).count()
        recent_purchases.append(CustomerPurchaseOut(
            id=p.id,
            policy_id=p.policy_id,
            policy_name=p.policy.name if p.policy else "N/A",
            policy_number=p.policy.policy_number if p.policy else "N/A",
            type=p.policy.type if p.policy else "N/A",
            premium=p.policy.premium if p.policy else 0.0,
            duration_months=p.policy.duration_months if p.policy else 0,
            start_date=p.start_date,
            end_date=p.end_date,
            status=p.status,
            created_at=p.created_at,
            claims_count=claims_count
        ))

    # Recent claims (last 5)
    recent_claims_raw = db.query(Claim).filter(
        Claim.customer_id == cid
    ).order_by(Claim.id.desc()).limit(5).all()

    recent_claims = []
    for c in recent_claims_raw:
        docs_count = db.query(Document).filter(Document.claim_id == c.id).count()
        pol_name = c.policy_purchase.policy.name if c.policy_purchase and c.policy_purchase.policy else "N/A"
        pol_num = c.policy_purchase.policy.policy_number if c.policy_purchase and c.policy_purchase.policy else "N/A"
        recent_claims.append(CustomerClaimOut(
            id=c.id,
            claim_number=c.claim_number,
            policy_purchase_id=c.policy_purchase_id,
            policy_name=pol_name,
            policy_number=pol_num,
            reason=c.reason,
            amount=c.amount,
            claim_date=c.claim_date,
            status=c.status,
            created_at=c.created_at,
            documents_count=docs_count
        ))

    return CustomerDashboardResponse(
        customer_name=current_customer.full_name,
        total_policies=total_policies,
        active_policies=active_policies,
        expired_policies=expired_policies,
        total_claims=total_claims,
        pending_claims=pending_claims,
        approved_claims=approved_claims,
        rejected_claims=rejected_claims,
        unread_notifications=unread_notifs,
        recent_purchases=recent_purchases,
        recent_claims=recent_claims
    )
