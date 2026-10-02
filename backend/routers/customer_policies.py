from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Policy, User
from schemas import PolicyOut, PolicyListResponse
from dependencies import require_customer

router = APIRouter(prefix="/api/customer/policies", tags=["Customer Policies"])

@router.get("", response_model=PolicyListResponse)
def list_available_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    # Only active policies are available for customer purchase
    query = db.query(Policy).filter(Policy.status == "ACTIVE")

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Policy.policy_number.ilike(search_term),
                Policy.name.ilike(search_term),
                Policy.description.ilike(search_term)
            )
        )

    if type and type.upper() in ["HEALTH", "LIFE", "VEHICLE", "TRAVEL", "HOME"]:
        query = query.filter(Policy.type == type.upper())

    total = query.count()
    policies = query.order_by(Policy.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [PolicyOut.model_validate(p) for p in policies]

    return PolicyListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=PolicyOut)
def get_policy_details(
    id: int,
    db: Session = Depends(get_db),
    current_customer: User = Depends(require_customer)
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Insurance policy not found")
    return PolicyOut.model_validate(policy)
