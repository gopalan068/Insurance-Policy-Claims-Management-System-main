from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, Claim, ClaimReview, Document
from schemas import (
    OfficerClaimOut,
    OfficerClaimDetailOut,
    OfficerClaimListResponse,
    DocumentOut,
    ClaimReviewOut,
    UserOut
)
from dependencies import require_claims_officer

router = APIRouter(prefix="/api/officer/claims", tags=["Officer Claims"])


def format_officer_claim_out(c: Claim, db: Session) -> OfficerClaimOut:
    docs_count = db.query(Document).filter(Document.claim_id == c.id).count()
    reviews_count = db.query(ClaimReview).filter(ClaimReview.claim_id == c.id).count()
    pol = c.policy_purchase.policy if c.policy_purchase and c.policy_purchase.policy else None
    return OfficerClaimOut(
        id=c.id,
        claim_number=c.claim_number,
        policy_purchase_id=c.policy_purchase_id,
        policy_name=pol.name if pol else "N/A",
        policy_number=pol.policy_number if pol else "N/A",
        policy_type=pol.type if pol else "N/A",
        reason=c.reason,
        amount=c.amount,
        claim_date=c.claim_date,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
        customer_name=c.customer.full_name if c.customer else "N/A",
        customer_email=c.customer.email if c.customer else "N/A",
        documents_count=docs_count,
        reviews_count=reviews_count
    )


@router.get("", response_model=OfficerClaimListResponse)
def list_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    officer: User = Depends(require_claims_officer)
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

    items = [format_officer_claim_out(c, db) for c in claims]

    return OfficerClaimListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{id}", response_model=OfficerClaimDetailOut)
def get_claim_details(
    id: int,
    db: Session = Depends(get_db),
    officer: User = Depends(require_claims_officer)
):
    claim = db.query(Claim).filter(Claim.id == id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Documents
    docs = db.query(Document).filter(Document.claim_id == claim.id).order_by(Document.id.desc()).all()
    docs_out = [DocumentOut.model_validate(d) for d in docs]

    # Reviews
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

    # Policy data
    pol = claim.policy_purchase.policy if claim.policy_purchase and claim.policy_purchase.policy else None
    pp = claim.policy_purchase

    return OfficerClaimDetailOut(
        id=claim.id,
        claim_number=claim.claim_number,
        policy_purchase_id=claim.policy_purchase_id,
        reason=claim.reason,
        amount=claim.amount,
        claim_date=claim.claim_date,
        status=claim.status,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        customer_name=claim.customer.full_name if claim.customer else "N/A",
        customer_email=claim.customer.email if claim.customer else "N/A",
        customer_phone=claim.customer.phone if claim.customer else None,
        policy_name=pol.name if pol else None,
        policy_number=pol.policy_number if pol else None,
        policy_type=pol.type if pol else None,
        policy_premium=pol.premium if pol else None,
        policy_duration_months=pol.duration_months if pol else None,
        policy_start_date=pp.start_date if pp else None,
        policy_end_date=pp.end_date if pp else None,
        documents=docs_out,
        reviews=reviews_out
    )
