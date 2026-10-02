from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Claim, User, Policy, PolicyPurchase, Document, ClaimReview
from schemas import (
    ClaimDetailOut,
    ClaimListResponse,
    PurchaseCustomerOut,
    PurchaseDetailOut,
    PurchasePolicyOut,
    PurchaseAgentOut,
    DocumentOut,
    ClaimReviewOut,
    UserOut
)
from dependencies import require_admin

router = APIRouter(prefix="/api/admin/claims", tags=["Admin Claims"])

def format_claim_detail(c: Claim, db: Session, include_relations: bool = True) -> ClaimDetailOut:
    customer_data = None
    if c.customer:
        customer_data = PurchaseCustomerOut(
            id=c.customer.id,
            full_name=c.customer.full_name,
            email=c.customer.email,
            phone=c.customer.phone
        )

    purchase_data = None
    if c.policy_purchase:
        p = c.policy_purchase
        pol_out = PurchasePolicyOut(
            id=p.policy.id,
            policy_number=p.policy.policy_number,
            name=p.policy.name,
            type=p.policy.type,
            premium=p.policy.premium,
            duration_months=p.policy.duration_months
        ) if p.policy else None

        agent_out = PurchaseAgentOut(
            id=p.agent.id,
            full_name=p.agent.full_name,
            email=p.agent.email
        ) if p.agent else None

        purchase_data = PurchaseDetailOut(
            id=p.id,
            policy_id=p.policy_id,
            customer_id=p.customer_id,
            agent_id=p.agent_id,
            start_date=p.start_date,
            end_date=p.end_date,
            status=p.status,
            created_at=p.created_at,
            customer=customer_data,
            policy=pol_out,
            agent=agent_out,
            claims_count=0
        )

    docs_out = []
    reviews_out = []
    if include_relations:
        docs = db.query(Document).filter(Document.claim_id == c.id).all()
        docs_out = [DocumentOut.model_validate(d) for d in docs]

        reviews = db.query(ClaimReview).filter(ClaimReview.claim_id == c.id).order_by(ClaimReview.id.desc()).all()
        for rev in reviews:
            officer_out = UserOut.model_validate(rev.officer) if rev.officer else None
            reviews_out.append(ClaimReviewOut(
                id=rev.id,
                claim_id=rev.claim_id,
                officer_id=rev.officer_id,
                decision=rev.decision,
                remarks=rev.remarks,
                review_date=rev.review_date,
                officer=officer_out
            ))

    return ClaimDetailOut(
        id=c.id,
        claim_number=c.claim_number,
        policy_purchase_id=c.policy_purchase_id,
        customer_id=c.customer_id,
        reason=c.reason,
        amount=c.amount,
        claim_date=c.claim_date,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        customer=customer_data,
        policy_purchase=purchase_data,
        documents=docs_out,
        reviews=reviews_out
    )

@router.get("", response_model=ClaimListResponse)
def list_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(Claim).join(Claim.customer)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Claim.claim_number.ilike(search_term),
                Claim.reason.ilike(search_term),
                User.full_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    if status and status.upper() in ["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]:
        query = query.filter(Claim.status == status.upper())

    total = query.count()
    claims = query.order_by(Claim.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [format_claim_detail(c, db, include_relations=True) for c in claims]

    return ClaimListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=ClaimDetailOut)
def get_claim_by_id(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    claim = db.query(Claim).filter(Claim.id == id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return format_claim_detail(claim, db, include_relations=True)
