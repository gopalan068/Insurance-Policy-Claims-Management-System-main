from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, PolicyPurchase, Claim, Document
from dependencies import require_agent

router = APIRouter(prefix="/api/agent/claims", tags=["Agent Claims"])


@router.get("")
def get_agent_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    # Get agent's purchase IDs
    agent_purchase_ids = [
        p.id for p in db.query(PolicyPurchase).filter(PolicyPurchase.agent_id == aid).all()
    ]

    if not agent_purchase_ids:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    query = db.query(Claim).filter(Claim.policy_purchase_id.in_(agent_purchase_ids))

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(Claim.claim_number.ilike(search_term), Claim.reason.ilike(search_term))
        )

    if status and status.upper() in ["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]:
        query = query.filter(Claim.status == status.upper())

    total = query.count()
    claims = query.order_by(Claim.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for c in claims:
        pol = c.policy_purchase.policy if c.policy_purchase and c.policy_purchase.policy else None
        cust = c.customer
        docs_count = db.query(Document).filter(Document.claim_id == c.id).count()
        items.append({
            "id": c.id,
            "claim_number": c.claim_number,
            "policy_name": pol.name if pol else "N/A",
            "policy_number": pol.policy_number if pol else "N/A",
            "customer_name": cust.full_name if cust else "N/A",
            "amount": c.amount,
            "reason": c.reason,
            "status": c.status,
            "claim_date": c.claim_date,
            "documents_count": docs_count,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{claim_id}")
def get_claim_detail(
    claim_id: int,
    db: Session = Depends(get_db),
    agent: User = Depends(require_agent)
):
    aid = agent.id

    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Verify this claim belongs to agent's purchase
    if not claim.policy_purchase or claim.policy_purchase.agent_id != aid:
        raise HTTPException(status_code=403, detail="Access denied: This claim is not related to your assignments")

    pol = claim.policy_purchase.policy if claim.policy_purchase and claim.policy_purchase.policy else None
    cust = claim.customer
    docs = db.query(Document).filter(Document.claim_id == claim.id).all()

    return {
        "id": claim.id,
        "claim_number": claim.claim_number,
        "amount": claim.amount,
        "reason": claim.reason,
        "status": claim.status,
        "claim_date": claim.claim_date,
        "customer": {
            "id": cust.id if cust else None,
            "full_name": cust.full_name if cust else "N/A",
            "email": cust.email if cust else "N/A",
            "phone": cust.phone if cust else None,
        },
        "policy": {
            "policy_number": pol.policy_number if pol else "N/A",
            "name": pol.name if pol else "N/A",
            "type": pol.type if pol else "N/A",
            "premium": pol.premium if pol else 0,
        },
        "documents": [{
            "id": d.id,
            "file_name": d.file_name,
            "file_type": d.file_type,
            "uploaded_date": d.uploaded_date,
        } for d in docs],
    }
