from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Policy, PolicyPurchase, User
from schemas import (
    PolicyCreate,
    PolicyUpdate,
    PolicyStatusUpdate,
    PolicyOut,
    PolicyListResponse,
    GenericMessageResponse
)
from dependencies import require_admin, log_audit_action

router = APIRouter(prefix="/api/admin/policies", tags=["Admin Policies"])

def format_policy_out(p: Policy, db: Session) -> PolicyOut:
    purchases_count = db.query(PolicyPurchase).filter(PolicyPurchase.policy_id == p.id).count()
    return PolicyOut(
        id=p.id,
        policy_number=p.policy_number,
        name=p.name,
        type=p.type,
        description=p.description,
        premium=p.premium,
        duration_months=p.duration_months,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        purchases_count=purchases_count
    )

@router.get("", response_model=PolicyListResponse)
def list_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(Policy)

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

    if status and status.upper() in ["ACTIVE", "INACTIVE"]:
        query = query.filter(Policy.status == status.upper())

    total = query.count()
    policies = query.order_by(Policy.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [format_policy_out(p, db) for p in policies]

    return PolicyListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=PolicyOut)
def get_policy_by_id(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return format_policy_out(policy, db)

@router.post("", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: PolicyCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Check duplicate policy number
    existing = db.query(Policy).filter(Policy.policy_number == payload.policy_number.strip().upper()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A policy with this policy number already exists"
        )

    if payload.premium <= 0:
        raise HTTPException(status_code=422, detail="Premium must be greater than zero")
    if payload.duration_months <= 0:
        raise HTTPException(status_code=422, detail="Duration months must be greater than zero")

    new_policy = Policy(
        policy_number=payload.policy_number.strip().upper(),
        name=payload.name.strip(),
        type=payload.type.upper(),
        description=payload.description.strip() if payload.description else None,
        premium=float(payload.premium),
        duration_months=int(payload.duration_months),
        status=payload.status.upper()
    )
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="CREATE_POLICY",
        target_type="POLICY",
        target_id=str(new_policy.id),
        details=f"Created policy {new_policy.policy_number} - {new_policy.name}"
    )

    return format_policy_out(new_policy, db)

@router.put("/{id}", response_model=PolicyOut)
def update_policy(
    id: int,
    payload: PolicyUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if payload.policy_number and payload.policy_number.strip().upper() != policy.policy_number:
        existing = db.query(Policy).filter(Policy.policy_number == payload.policy_number.strip().upper()).first()
        if existing and existing.id != policy.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Policy number already in use by another policy"
            )
        policy.policy_number = payload.policy_number.strip().upper()

    if payload.name is not None:
        policy.name = payload.name.strip()
    if payload.type is not None:
        policy.type = payload.type.upper()
    if payload.description is not None:
        policy.description = payload.description.strip() if payload.description else None
    if payload.premium is not None:
        if payload.premium <= 0:
            raise HTTPException(status_code=422, detail="Premium must be greater than zero")
        policy.premium = float(payload.premium)
    if payload.duration_months is not None:
        if payload.duration_months <= 0:
            raise HTTPException(status_code=422, detail="Duration months must be greater than zero")
        policy.duration_months = int(payload.duration_months)
    if payload.status is not None:
        policy.status = payload.status.upper()

    db.commit()
    db.refresh(policy)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="UPDATE_POLICY",
        target_type="POLICY",
        target_id=str(policy.id),
        details=f"Updated policy {policy.policy_number}"
    )

    return format_policy_out(policy, db)

@router.patch("/{id}/status", response_model=PolicyOut)
def update_policy_status(
    id: int,
    payload: PolicyStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.status = payload.status.upper()
    db.commit()
    db.refresh(policy)

    action_label = "ACTIVATE_POLICY" if payload.status.upper() == "ACTIVE" else "DEACTIVATE_POLICY"
    log_audit_action(
        db=db,
        admin_id=admin.id,
        action=action_label,
        target_type="POLICY",
        target_id=str(policy.id),
        details=f"Changed status of policy {policy.policy_number} to {payload.status}"
    )

    return format_policy_out(policy, db)

@router.delete("/{id}", response_model=GenericMessageResponse)
def delete_policy(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Check if policy has active purchases
    active_purchases = db.query(PolicyPurchase).filter(
        PolicyPurchase.policy_id == id,
        PolicyPurchase.status == "ACTIVE"
    ).count()

    if active_purchases > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete policy with {active_purchases} active customer purchases. Deactivate the policy instead."
        )

    pol_num = policy.policy_number
    db.delete(policy)
    db.commit()

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="DELETE_POLICY",
        target_type="POLICY",
        target_id=str(id),
        details=f"Deleted policy {pol_num}"
    )

    return GenericMessageResponse(message=f"Policy {pol_num} deleted successfully")
