from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, PolicyPurchase, Policy
from schemas import (
    AgentCreate,
    AgentUpdate,
    UserStatusUpdate,
    AgentDetailOut,
    AgentListResponse,
    GenericMessageResponse
)
from auth import hash_password
from dependencies import require_admin, log_audit_action

router = APIRouter(prefix="/api/admin/agents", tags=["Admin Agents"])

def format_agent_detail(agent: User, db: Session) -> AgentDetailOut:
    purchases = db.query(PolicyPurchase).filter(PolicyPurchase.agent_id == agent.id).all()
    total_premium = 0.0
    for p in purchases:
        if p.policy and p.policy.premium:
            total_premium += float(p.policy.premium)

    return AgentDetailOut(
        id=agent.id,
        full_name=agent.full_name,
        email=agent.email,
        phone=agent.phone,
        role=agent.role,
        is_active=agent.is_active,
        created_at=agent.created_at,
        purchases_handled_count=len(purchases),
        total_premium_generated=round(total_premium, 2)
    )

@router.get("", response_model=AgentListResponse)
def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    query = db.query(User).filter(User.role == "AGENT")

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
    agents = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [format_agent_detail(a, db) for a in agents]

    return AgentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{id}", response_model=AgentDetailOut)
def get_agent_by_id(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    agent = db.query(User).filter(User.id == id, User.role == "AGENT").first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return format_agent_detail(agent, db)

@router.post("", response_model=AgentDetailOut, status_code=status.HTTP_201_CREATED)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists"
        )
    
    new_agent = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower().strip(),
        phone=payload.phone.strip() if payload.phone else None,
        password_hash=hash_password(payload.password),
        role="AGENT",
        is_active=payload.is_active
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="CREATE_AGENT",
        target_type="AGENT",
        target_id=str(new_agent.id),
        details=f"Created agent account {new_agent.full_name} ({new_agent.email})"
    )

    return format_agent_detail(new_agent, db)

@router.put("/{id}", response_model=AgentDetailOut)
def update_agent(
    id: int,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    agent = db.query(User).filter(User.id == id, User.role == "AGENT").first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if payload.email and payload.email.lower().strip() != agent.email:
        existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
        if existing and existing.id != agent.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already taken"
            )
        agent.email = payload.email.lower().strip()

    if payload.full_name is not None:
        agent.full_name = payload.full_name.strip()
    if payload.phone is not None:
        agent.phone = payload.phone.strip() if payload.phone else None
    if payload.is_active is not None:
        agent.is_active = payload.is_active
    if payload.password:
        agent.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(agent)

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="UPDATE_AGENT",
        target_type="AGENT",
        target_id=str(agent.id),
        details=f"Updated agent {agent.email}"
    )

    return format_agent_detail(agent, db)

@router.patch("/{id}/status", response_model=AgentDetailOut)
def update_agent_status(
    id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    agent = db.query(User).filter(User.id == id, User.role == "AGENT").first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.is_active = payload.is_active
    db.commit()
    db.refresh(agent)

    action_label = "ACTIVATE_AGENT" if payload.is_active else "DEACTIVATE_AGENT"
    log_audit_action(
        db=db,
        admin_id=admin.id,
        action=action_label,
        target_type="AGENT",
        target_id=str(agent.id),
        details=f"Changed active status of agent {agent.email} to {payload.is_active}"
    )

    return format_agent_detail(agent, db)

@router.delete("/{id}", response_model=GenericMessageResponse)
def delete_agent(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    agent = db.query(User).filter(User.id == id, User.role == "AGENT").first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent_email = agent.email
    db.delete(agent)
    db.commit()

    log_audit_action(
        db=db,
        admin_id=admin.id,
        action="DELETE_AGENT",
        target_type="AGENT",
        target_id=str(id),
        details=f"Deleted agent account {agent_email}"
    )

    return GenericMessageResponse(message=f"Agent {agent_email} deleted successfully")
