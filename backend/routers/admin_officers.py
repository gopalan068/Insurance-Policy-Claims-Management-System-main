from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, ClaimReview
from schemas import (
    OfficerCreate,
    OfficerUpdate,
    UserStatusUpdate,
    OfficerDetailOut,
    OfficerListResponse,
    GenericMessageResponse
)
from auth import hash_password
from dependencies import require_admin, log_audit_action

router = APIRouter(prefix="/api/admin/claims-officers", tags=["Admin Claims Officers"])

def format_officer_detail(officer: User, db: Session) -> OfficerDetailOut:
    reviews = db.query(ClaimReview).filter(ClaimReview.officer_id == officer.id).all()
    approved = sum(1 for r in reviews if r.decision == "APPROVED")
    rejected = sum(1 for r in reviews if r.decision == "REJECTED")

    return OfficerDetailOut(
        id=officer.id,
        full_name=officer.full_name,
        email=officer.email,
        phone=officer.phone,
        role=officer.role,
        is_active=officer.is_active,
        created_at=officer.created_at,
        reviews_count=len(reviews),
        approved_count=approved,
        rejected_count=rejected
    )

@router.get("", response_model=OfficerListResponse)
def list_claims_officers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(User).filter(User.role == "CLAIMS_OFFICER")

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.phone.ilike(search_term)
            )
        )

    if status is not None and status != "":
        if status.lower() in ["active", "true", "1"]:
            query = query.filter(User.is_active == True)
        elif status.lower() in ["inactive", "false", "0"]:
            query = query.filter(User.is_active == False)

    total = query.count()
    officers = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [format_officer_detail(o, db) for o in officers]

    return OfficerListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=OfficerDetailOut)
def get_claims_officer_by_id(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    officer = db.query(User).filter(User.id == id, User.role == "CLAIMS_OFFICER").first()
    if not officer:
        raise HTTPException(status_code=404, detail="Claims Officer not found")
    return format_officer_detail(officer, db)

@router.post("", response_model=OfficerDetailOut, status_code=status.HTTP_201_CREATED)
def create_claims_officer(
    payload: OfficerCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists"
        )
    
    new_officer = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone.strip() if payload.phone else None,
        password_hash=hash_password(payload.password),
        role="CLAIMS_OFFICER",
        is_active=payload.is_active
    )
    db.add(new_officer)
    db.commit()
    db.refresh(new_officer)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="CREATE_CLAIMS_OFFICER",
        target_type="CLAIMS_OFFICER",
        target_id=str(new_officer.id),
        details=f"Created claims officer {new_officer.full_name} ({new_officer.email})"
    )

    return format_officer_detail(new_officer, db)

@router.put("/{id}", response_model=OfficerDetailOut)
def update_claims_officer(
    id: int,
    payload: OfficerUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    officer = db.query(User).filter(User.id == id, User.role == "CLAIMS_OFFICER").first()
    if not officer:
        raise HTTPException(status_code=404, detail="Claims Officer not found")

    if payload.email and payload.email.lower().strip() != officer.email:
        existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
        if existing and existing.id != officer.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already taken"
            )
        officer.email = payload.email.lower().strip()

    if payload.full_name is not None:
        officer.full_name = payload.full_name.strip()
    if payload.phone is not None:
        officer.phone = payload.phone.strip() if payload.phone else None
    if payload.is_active is not None:
        officer.is_active = payload.is_active
    if payload.password:
        officer.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(officer)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="UPDATE_CLAIMS_OFFICER",
        target_type="CLAIMS_OFFICER",
        target_id=str(officer.id),
        details=f"Updated claims officer {officer.email}"
    )

    return format_officer_detail(officer, db)

@router.patch("/{id}/status", response_model=OfficerDetailOut)
def update_claims_officer_status(
    id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    officer = db.query(User).filter(User.id == id, User.role == "CLAIMS_OFFICER").first()
    if not officer:
        raise HTTPException(status_code=404, detail="Claims Officer not found")

    officer.is_active = payload.is_active
    db.commit()
    db.refresh(officer)

    action_label = "ACTIVATE_CLAIMS_OFFICER" if payload.is_active else "DEACTIVATE_CLAIMS_OFFICER"
    log_audit_action(
        db=db,
        admin_id=admin.id,
        action=action_label,
        target_type="CLAIMS_OFFICER",
        target_id=str(officer.id),
        details=f"Changed active status of claims officer {officer.email} to {payload.is_active}"
    )

    return format_officer_detail(officer, db)

@router.delete("/{id}", response_model=GenericMessageResponse)
def delete_claims_officer(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    officer = db.query(User).filter(User.id == id, User.role == "CLAIMS_OFFICER").first()
    if not officer:
        raise HTTPException(status_code=404, detail="Claims Officer not found")

    officer_email = officer.email
    db.delete(officer)
    db.commit()

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="DELETE_CLAIMS_OFFICER",
        target_type="CLAIMS_OFFICER",
        target_id=str(id),
        details=f"Deleted claims officer {officer_email}"
    )

    return GenericMessageResponse(message=f"Claims Officer {officer_email} deleted successfully")
