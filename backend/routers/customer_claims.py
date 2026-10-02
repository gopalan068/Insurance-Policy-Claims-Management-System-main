from datetime import datetime, timezone
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import PolicyPurchase, Claim, User, Document, ClaimReview
from schemas import (
    CustomerClaimCreate,
    CustomerClaimOut,
    CustomerClaimDetailOut,
    DocumentOut,
    ClaimReviewOut,
    UserOut
)
from dependencies import require_customer, log_audit_action, create_notification

router = APIRouter(prefix="/api/customer/claims", tags=["Customer Claims"])

def utc_now():
    return datetime.now(timezone.utc)

def generate_unique_claim_number(db: Session) -> str:
    year = datetime.now().year
    for _ in range(50):
        rand_num = random.randint(1000, 9999)
        candidate = f"CLM-{year}-{rand_num}"
        existing = db.query(Claim).filter(Claim.claim_number == candidate).first()
        if not existing:
            return candidate
    # Fallback with timestamp millis
    return f"CLM-{year}-{int(datetime.now().timestamp()) % 100000}"

@router.post("", response_model=CustomerClaimDetailOut, status_code=status.HTTP_201_CREATED)
def submit_claim(
    payload: CustomerClaimCreate,
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    # Strict validation: Purchase must exist and belong to current customer
    purchase = db.query(PolicyPurchase).filter(
        PolicyPurchase.id == payload.policy_purchase_id,
        PolicyPurchase.customer_id == current_customer.id
    ).first()

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valid policy purchase not found or does not belong to your account."
        )

    if purchase.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot file a claim on a policy with status '{purchase.status}'. Only active policies are eligible for claims."
        )

    if payload.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Claim amount must be greater than zero."
        )

    claim_num = generate_unique_claim_number(db)
    claim_dt = payload.incident_date or utc_now()
    now = utc_now()

    new_claim = Claim(
        claim_number=claim_num,
        policy_purchase_id=purchase.id,
        customer_id=current_customer.id,
        reason=payload.reason.strip(),
        amount=float(payload.amount),
        claim_date=claim_dt,
        status="SUBMITTED",
        created_at=now,
        updated_at=now
    )
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)

    # Customer Notification
    create_notification(
        db=db,
        user_id=current_customer.id,
        title="Claim Filed Successfully",
        message=f"Claim {new_claim.claim_number} for ${new_claim.amount:,.2f} has been submitted and registered for Claims Officer review.",
        notification_type="INFO",
        link=f"/customer/claims/{new_claim.id}"
    )

    # Audit Trail
    log_audit_action(
        db=db,
        admin_id=None,
        action="CLAIM_SUBMITTED",
        target_type="CLAIM",
        target_id=str(new_claim.id),
        details=f"Customer {current_customer.full_name} submitted claim {new_claim.claim_number} (${new_claim.amount})."
    )

    pol = purchase.policy
    return CustomerClaimDetailOut(
        id=new_claim.id,
        claim_number=new_claim.claim_number,
        policy_purchase_id=new_claim.policy_purchase_id,
        policy_name=pol.name if pol else "N/A",
        policy_number=pol.policy_number if pol else "N/A",
        policy_type=pol.type if pol else "N/A",
        reason=new_claim.reason,
        amount=new_claim.amount,
        claim_date=new_claim.claim_date,
        status=new_claim.status,
        created_at=new_claim.created_at,
        updated_at=new_claim.updated_at,
        documents=[],
        reviews=[]
    )

@router.get("", response_model=List[CustomerClaimOut])
def get_my_claims(
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    claims = db.query(Claim).filter(
        Claim.customer_id == current_customer.id
    ).order_by(Claim.id.desc()).all()

    result = []
    for c in claims:
        docs_count = db.query(Document).filter(Document.claim_id == c.id).count()
        pol_name = c.policy_purchase.policy.name if c.policy_purchase and c.policy_purchase.policy else "N/A"
        pol_num = c.policy_purchase.policy.policy_number if c.policy_purchase and c.policy_purchase.policy else "N/A"
        result.append(CustomerClaimOut(
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

    return result

@router.get("/{id}", response_model=CustomerClaimDetailOut)
def get_my_claim_details(
    id: int,
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    # Strict IDOR check: Claim must belong to current customer
    claim = db.query(Claim).filter(
        Claim.id == id,
        Claim.customer_id == current_customer.id
    ).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim record not found or access denied."
        )

    # Documents for this claim
    docs = db.query(Document).filter(Document.claim_id == claim.id).order_by(Document.id.desc()).all()
    docs_out = [DocumentOut.model_validate(d) for d in docs]

    # Officer review remarks for this claim
    reviews = db.query(ClaimReview).filter(ClaimReview.claim_id == claim.id).order_by(ClaimReview.id.desc()).all()
    reviews_out = []
    for r in reviews:
        officer_out = UserOut.model_validate(r.officer) if r.officer else None
        reviews_out.append(ClaimReviewOut(
            id=r.id,
            claim_id=r.claim_id,
            officer_id=r.officer_id,
            decision=r.decision,
            remarks=r.remarks,
            review_date=r.review_date,
            officer=officer_out
        ))

    pol = claim.policy_purchase.policy if claim.policy_purchase else None

    return CustomerClaimDetailOut(
        id=claim.id,
        claim_number=claim.claim_number,
        policy_purchase_id=claim.policy_purchase_id,
        policy_name=pol.name if pol else "N/A",
        policy_number=pol.policy_number if pol else "N/A",
        policy_type=pol.type if pol else "N/A",
        reason=claim.reason,
        amount=claim.amount,
        claim_date=claim.claim_date,
        status=claim.status,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        documents=docs_out,
        reviews=reviews_out
    )
