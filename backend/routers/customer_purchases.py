from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Policy, PolicyPurchase, User, Claim
from schemas import (
    CustomerPurchaseCreate,
    CustomerPurchaseOut,
    CustomerPurchaseDetailOut
)
from dependencies import require_customer, log_audit_action, create_notification

router = APIRouter(prefix="/api/customer/purchases", tags=["Customer Policy Purchases"])

def utc_now():
    return datetime.now(timezone.utc)

@router.post("", response_model=CustomerPurchaseDetailOut, status_code=status.HTTP_201_CREATED)
def purchase_policy(
    payload: CustomerPurchaseCreate,
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    policy = db.query(Policy).filter(Policy.id == payload.policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Insurance policy plan not found.")
    
    if policy.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This policy is currently inactive and cannot be purchased."
        )

    # Calculate coverage span based on duration_months
    start_time = utc_now()
    # 1 month approx 30.5 days
    end_time = start_time + timedelta(days=int(policy.duration_months * 30.5))

    new_purchase = PolicyPurchase(
        policy_id=policy.id,
        customer_id=current_customer.id,
        agent_id=None,  # Direct purchase via Customer portal
        start_date=start_time,
        end_date=end_time,
        status="ACTIVE",
        created_at=start_time
    )
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)

    # Create Notification for Customer
    create_notification(
        db=db,
        user_id=current_customer.id,
        title="Policy Purchase Successful",
        message=f"You have successfully purchased {policy.name} ({policy.policy_number}). Your coverage is active until {end_time.strftime('%b %d, %Y')}.",
        notification_type="SUCCESS",
        link=f"/customer/policies/my/{new_purchase.id}"
    )

    # Log Audit Trail
    log_audit_action(
        db=db,
        admin_id=None,
        action="POLICY_PURCHASED",
        target_type="POLICY_PURCHASE",
        target_id=str(new_purchase.id),
        details=f"Customer {current_customer.full_name} purchased policy {policy.policy_number} for ${policy.premium}."
    )

    return CustomerPurchaseDetailOut(
        id=new_purchase.id,
        policy_id=policy.id,
        policy_name=policy.name,
        policy_number=policy.policy_number,
        type=policy.type,
        description=policy.description,
        premium=policy.premium,
        duration_months=policy.duration_months,
        start_date=new_purchase.start_date,
        end_date=new_purchase.end_date,
        status=new_purchase.status,
        created_at=new_purchase.created_at,
        agent_name="Direct Online Purchase",
        claims=[]
    )

@router.get("", response_model=List[CustomerPurchaseOut])
def get_my_purchases(
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    purchases = db.query(PolicyPurchase).filter(
        PolicyPurchase.customer_id == current_customer.id
    ).order_by(PolicyPurchase.id.desc()).all()

    result = []
    for p in purchases:
        claims_count = db.query(Claim).filter(Claim.policy_purchase_id == p.id).count()
        result.append(CustomerPurchaseOut(
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

    return result

@router.get("/{id}", response_model=CustomerPurchaseDetailOut)
def get_my_purchase_details(
    id: int,
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    # Strict IDOR check: customer can only fetch their own purchase
    purchase = db.query(PolicyPurchase).filter(
        PolicyPurchase.id == id,
        PolicyPurchase.customer_id == current_customer.id
    ).first()

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy purchase record not found or access denied."
        )

    claims = db.query(Claim).filter(Claim.policy_purchase_id == purchase.id).all()
    claims_list = [
        {
            "id": c.id,
            "claim_number": c.claim_number,
            "reason": c.reason,
            "amount": c.amount,
            "claim_date": c.claim_date,
            "status": c.status
        }
        for c in claims
    ]

    agent_name = purchase.agent.full_name if purchase.agent else "Direct Online Purchase"

    return CustomerPurchaseDetailOut(
        id=purchase.id,
        policy_id=purchase.policy_id,
        policy_name=purchase.policy.name if purchase.policy else "N/A",
        policy_number=purchase.policy.policy_number if purchase.policy else "N/A",
        type=purchase.policy.type if purchase.policy else "N/A",
        description=purchase.policy.description if purchase.policy else None,
        premium=purchase.policy.premium if purchase.policy else 0.0,
        duration_months=purchase.policy.duration_months if purchase.policy else 0,
        start_date=purchase.start_date,
        end_date=purchase.end_date,
        status=purchase.status,
        created_at=purchase.created_at,
        agent_name=agent_name,
        claims=claims_list
    )
