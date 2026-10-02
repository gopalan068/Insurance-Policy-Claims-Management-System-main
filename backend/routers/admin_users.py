from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, PolicyPurchase, Claim, ClaimReview
from schemas import (
    UserCreate,
    UserUpdate,
    UserStatusUpdate,
    UserDetailOut,
    UserListResponse,
    GenericMessageResponse
)
from auth import hash_password
from dependencies import require_admin, log_audit_action

router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])

def get_user_detail_schema(u: User, db: Session) -> UserDetailOut:
    policies_count = db.query(PolicyPurchase).filter(PolicyPurchase.customer_id == u.id).count()
    claims_count = db.query(Claim).filter(Claim.customer_id == u.id).count()
    purchases_handled_count = db.query(PolicyPurchase).filter(PolicyPurchase.agent_id == u.id).count()
    reviews_count = db.query(ClaimReview).filter(ClaimReview.officer_id == u.id).count()

    return UserDetailOut(
        id=u.id,
        full_name=u.full_name,
        email=u.email,
        phone=u.phone,
        role=u.role,
        is_active=u.is_active,
        created_at=u.created_at,
        updated_at=u.updated_at,
        policies_count=policies_count,
        claims_count=claims_count,
        purchases_handled_count=purchases_handled_count,
        reviews_count=reviews_count
    )

@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(User)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.phone.ilike(search_term)
            )
        )

    if role and role.upper() in ["ADMIN", "CUSTOMER", "AGENT", "CLAIMS_OFFICER"]:
        query = query.filter(User.role == role.upper())

    if status is not None and status != "":
        if status.lower() in ["active", "true", "1"]:
            query = query.filter(User.is_active == True)
        elif status.lower() in ["inactive", "false", "0"]:
            query = query.filter(User.is_active == False)

    total = query.count()
    users = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [get_user_detail_schema(u, db) for u in users]

    return UserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=UserDetailOut)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_user_detail_schema(user, db)

@router.post("", response_model=UserDetailOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Check duplicate email
    existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists"
        )
    
    new_user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone.strip() if payload.phone else None,
        password_hash=hash_password(payload.password),
        role=payload.role.upper(),
        is_active=payload.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="CREATE_USER",
        target_type="USER",
        target_id=str(new_user.id),
        details=f"Created user {new_user.full_name} ({new_user.email}) with role {new_user.role}"
    )

    return get_user_detail_schema(new_user, db)

@router.put("/{id}", response_model=UserDetailOut)
def update_user(
    id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email and payload.email.lower().strip() != user.email:
        existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already in use by another user"
            )
        user.email = payload.email.lower().strip()

    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()
    if payload.phone is not None:
        user.phone = payload.phone.strip() if payload.phone else None
    if payload.role is not None:
        user.role = payload.role.upper()
    if payload.is_active is not None:
        if user.id == admin.id and not payload.is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate your own currently logged in account"
            )
        user.is_active = payload.is_active
    if payload.password:
        user.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(user)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="UPDATE_USER",
        target_type="USER",
        target_id=str(user.id),
        details=f"Updated profile for user {user.email}"
    )

    return get_user_detail_schema(user, db)

@router.patch("/{id}/status", response_model=UserDetailOut)
def update_user_status(
    id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin.id and not payload.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own currently logged in account"
        )

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)

    action_label = "ACTIVATE_USER" if payload.is_active else "DEACTIVATE_USER"
    log_audit_action(
        db=db,
        admin_id=admin.id,
        action=action_label,
        target_type="USER",
        target_id=str(user.id),
        details=f"Changed active status of user {user.email} to {payload.is_active}"
    )

    return get_user_detail_schema(user, db)

@router.delete("/{id}", response_model=GenericMessageResponse)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own currently logged in admin account"
        )

    user_email = user.email
    db.delete(user)
    db.commit()

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="DELETE_USER",
        target_type="USER",
        target_id=str(id),
        details=f"Deleted user account {user_email}"
    )

    return GenericMessageResponse(message=f"User {user_email} deleted successfully")
