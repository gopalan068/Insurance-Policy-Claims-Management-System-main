from datetime import datetime, timezone
from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Policy, PolicyPurchase, Claim
from schemas import (
    DashboardStatsResponse,
    ClaimsByStatusStat,
    PoliciesByTypeStat,
    MonthlyClaimsStat,
    PremiumRevenueStat
)
from dependencies import require_admin

router = APIRouter(prefix="/api/admin/dashboard", tags=["Admin Dashboard"])

@router.get("", response_model=DashboardStatsResponse)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Total counts
    total_users = db.query(User).count()
    total_customers = db.query(User).filter(User.role == "CUSTOMER").count()
    total_agents = db.query(User).filter(User.role == "AGENT").count()
    total_claims_officers = db.query(User).filter(User.role == "CLAIMS_OFFICER").count()

    total_policies = db.query(Policy).count()
    active_policies = db.query(Policy).filter(Policy.status == "ACTIVE").count()

    total_policy_purchases = db.query(PolicyPurchase).count()
    expired_policies = db.query(PolicyPurchase).filter(PolicyPurchase.status == "EXPIRED").count()

    total_claims = db.query(Claim).count()
    pending_claims = db.query(Claim).filter(Claim.status.in_(["SUBMITTED", "UNDER_REVIEW"])).count()
    approved_claims = db.query(Claim).filter(Claim.status == "APPROVED").count()
    rejected_claims = db.query(Claim).filter(Claim.status == "REJECTED").count()

    # Chart 1: Claims by status
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

    # Chart 2: Policies by type
    policy_types = ["HEALTH", "LIFE", "VEHICLE", "TRAVEL", "HOME"]
    policies_by_type = []
    for p_type in policy_types:
        p_count = db.query(Policy).filter(Policy.type == p_type).count()
        purchases_count = db.query(PolicyPurchase).join(Policy).filter(Policy.type == p_type).count()
        policies_by_type.append(PoliciesByTypeStat(
            type=p_type,
            count=p_count,
            total_purchases=purchases_count
        ))

    # Chart 3: Monthly claims trend (past 6 months)
    all_claims = db.query(Claim).all()
    monthly_data = defaultdict(lambda: {"submitted": 0, "approved": 0, "rejected": 0, "amount": 0.0})
    
    for c in all_claims:
        if c.claim_date:
            month_key = c.claim_date.strftime("%b %Y")
        else:
            month_key = "Recent"
        
        if c.status == "APPROVED":
            monthly_data[month_key]["approved"] += 1
        elif c.status == "REJECTED":
            monthly_data[month_key]["rejected"] += 1
        else:
            monthly_data[month_key]["submitted"] += 1
        monthly_data[month_key]["amount"] += float(c.amount or 0)

    # Sort months chronologically or return list
    monthly_claims = [
        MonthlyClaimsStat(
            month=m,
            submitted_count=vals["submitted"],
            approved_count=vals["approved"],
            rejected_count=vals["rejected"],
            total_amount=round(vals["amount"], 2)
        )
        for m, vals in list(monthly_data.items())[-6:]
    ]

    # Chart 4: Premium Revenue by Policy Type
    purchases = db.query(PolicyPurchase).join(Policy).all()
    revenue_by_type = defaultdict(float)
    active_by_type = defaultdict(int)

    for pur in purchases:
        if pur.policy:
            p_type = pur.policy.type
            revenue_by_type[p_type] += float(pur.policy.premium or 0)
            if pur.status == "ACTIVE":
                active_by_type[p_type] += 1

    premium_revenue = [
        PremiumRevenueStat(
            policy_type=p_type,
            active_policies=active_by_type[p_type],
            total_revenue=round(revenue_by_type[p_type], 2)
        )
        for p_type in policy_types
    ]

    return DashboardStatsResponse(
        total_users=total_users,
        total_customers=total_customers,
        total_agents=total_agents,
        total_claims_officers=total_claims_officers,
        total_policies=total_policies,
        active_policies=active_policies,
        total_policy_purchases=total_policy_purchases,
        total_claims=total_claims,
        pending_claims=pending_claims,
        approved_claims=approved_claims,
        rejected_claims=rejected_claims,
        expired_policies=expired_policies,
        claims_by_status=claims_by_status,
        policies_by_type=policies_by_type,
        monthly_claims=monthly_claims,
        premium_revenue=premium_revenue
    )
