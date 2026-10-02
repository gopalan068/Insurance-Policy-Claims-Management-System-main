from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Claim, ClaimReview, Document
from schemas import OfficerDashboardResponse, ClaimsByStatusStat, OfficerClaimOut
from dependencies import require_claims_officer

router = APIRouter(prefix="/api/officer/dashboard", tags=["Officer Dashboard"])


def utc_now():
    return datetime.now(timezone.utc)


@router.get("", response_model=OfficerDashboardResponse)
def get_officer_dashboard(
    db: Session = Depends(get_db),
    officer: User = Depends(require_claims_officer)
):
    oid = officer.id

    # Claim metrics
    total_claims = db.query(Claim).count()
    submitted_claims = db.query(Claim).filter(Claim.status == "SUBMITTED").count()
    under_review_claims = db.query(Claim).filter(Claim.status == "UNDER_REVIEW").count()
    approved_claims = db.query(Claim).filter(Claim.status == "APPROVED").count()
    rejected_claims = db.query(Claim).filter(Claim.status == "REJECTED").count()

    # My reviews count
    my_reviews_count = db.query(ClaimReview).filter(ClaimReview.officer_id == oid).count()

    # Pending review claims (submitted or under review)
    pending_review_claims = db.query(Claim).filter(
        Claim.status.in_(["SUBMITTED", "UNDER_REVIEW"])
    ).count()

    # Claims by status for chart
    claims_by_status_raw = db.query(
        Claim.status,
        func.count(Claim.id).label("count"),
        func.coalesce(func.sum(Claim.amount), 0.0).label("total_amount")
    ).group_by(Claim.status).all()

    claims_status_map = {row[0]: (row[1], float(row[2])) for row in claims_by_status_raw}
    standard_statuses = ["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]
    claims_by_status = [
        ClaimsByStatusStat(
            status=st,
            count=claims_status_map.get(st, (0, 0.0))[0],
            total_amount=claims_status_map.get(st, (0, 0.0))[1]
        )
        for st in standard_statuses
    ]

    # Recent claims (last 10)
    recent_claims_raw = db.query(Claim).order_by(Claim.id.desc()).limit(10).all()
    recent_claims = []
    for c in recent_claims_raw:
        docs_count = db.query(Document).filter(Document.claim_id == c.id).count()
        reviews_count = db.query(ClaimReview).filter(ClaimReview.claim_id == c.id).count()
        pol = c.policy_purchase.policy if c.policy_purchase and c.policy_purchase.policy else None
        recent_claims.append(OfficerClaimOut(
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
        ))

    return OfficerDashboardResponse(
        officer_name=officer.full_name,
        total_claims=total_claims,
        submitted_claims=submitted_claims,
        under_review_claims=under_review_claims,
        approved_claims=approved_claims,
        rejected_claims=rejected_claims,
        my_reviews_count=my_reviews_count,
        pending_review_claims=pending_review_claims,
        claims_by_status=claims_by_status,
        recent_claims=recent_claims
    )
