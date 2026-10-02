from datetime import datetime, date
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ----------------- Base / Shared Schemas -----------------

class GenericMessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int

# ----------------- Auth Schemas -----------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ----------------- User Management Schemas -----------------

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(ADMIN|CUSTOMER|AGENT|CLAIMS_OFFICER)$")
    is_active: bool = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    role: Optional[str] = Field(None, pattern="^(ADMIN|CUSTOMER|AGENT|CLAIMS_OFFICER)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserDetailOut(UserOut):
    policies_count: Optional[int] = 0
    claims_count: Optional[int] = 0
    purchases_handled_count: Optional[int] = 0
    reviews_count: Optional[int] = 0

class UserListResponse(BaseModel):
    items: List[UserDetailOut]
    total: int
    page: int
    page_size: int

# ----------------- Customer Schemas -----------------

class CustomerDetailOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    policies_count: int
    claims_count: int
    policies: Optional[List[Any]] = []
    claims: Optional[List[Any]] = []

    model_config = ConfigDict(from_attributes=True)

class CustomerListResponse(BaseModel):
    items: List[CustomerDetailOut]
    total: int
    page: int
    page_size: int

# ----------------- Agent Schemas -----------------

class AgentCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    password: str = Field(..., min_length=6)
    is_active: bool = True

class AgentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)

class AgentDetailOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    purchases_handled_count: int
    total_premium_generated: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class AgentListResponse(BaseModel):
    items: List[AgentDetailOut]
    total: int
    page: int
    page_size: int

# ----------------- Claims Officer Schemas -----------------

class OfficerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    password: str = Field(..., min_length=6)
    is_active: bool = True

class OfficerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)

class OfficerDetailOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    reviews_count: int
    approved_count: int = 0
    rejected_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class OfficerListResponse(BaseModel):
    items: List[OfficerDetailOut]
    total: int
    page: int
    page_size: int

# ----------------- Policy Schemas -----------------

class PolicyCreate(BaseModel):
    policy_number: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=3, max_length=150)
    type: str = Field(..., pattern="^(HEALTH|LIFE|VEHICLE|TRAVEL|HOME)$")
    description: Optional[str] = None
    premium: float = Field(..., gt=0)
    duration_months: int = Field(..., gt=0)
    status: str = Field("ACTIVE", pattern="^(ACTIVE|INACTIVE)$")

class PolicyUpdate(BaseModel):
    policy_number: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    type: Optional[str] = Field(None, pattern="^(HEALTH|LIFE|VEHICLE|TRAVEL|HOME)$")
    description: Optional[str] = None
    premium: Optional[float] = Field(None, gt=0)
    duration_months: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE)$")

class PolicyStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|INACTIVE)$")

class PolicyOut(BaseModel):
    id: int
    policy_number: str
    name: str
    type: str
    description: Optional[str] = None
    premium: float
    duration_months: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    purchases_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class PolicyListResponse(BaseModel):
    items: List[PolicyOut]
    total: int
    page: int
    page_size: int

# ----------------- Policy Purchase Schemas -----------------

class PurchaseCustomerOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PurchaseAgentOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class PurchasePolicyOut(BaseModel):
    id: int
    policy_number: str
    name: str
    type: str
    premium: float
    duration_months: int

    model_config = ConfigDict(from_attributes=True)

class PurchaseDetailOut(BaseModel):
    id: int
    policy_id: int
    customer_id: int
    agent_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime
    customer: Optional[PurchaseCustomerOut] = None
    policy: Optional[PurchasePolicyOut] = None
    agent: Optional[PurchaseAgentOut] = None
    claims_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class PurchaseListResponse(BaseModel):
    items: List[PurchaseDetailOut]
    total: int
    page: int
    page_size: int

# ----------------- Document & Review Schemas -----------------

class DocumentOut(BaseModel):
    id: int
    claim_id: int
    file_name: str
    file_path: str
    file_type: str
    uploaded_date: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListResponse(BaseModel):
    items: List[DocumentOut]
    total: int
    page: int
    page_size: int

class ClaimReviewOut(BaseModel):
    id: int
    claim_id: int
    officer_id: int
    decision: str
    remarks: str
    review_date: datetime
    officer: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)

# ----------------- Claim Schemas -----------------

class ClaimDetailOut(BaseModel):
    id: int
    claim_number: str
    policy_purchase_id: int
    customer_id: int
    reason: str
    amount: float
    claim_date: datetime
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer: Optional[PurchaseCustomerOut] = None
    policy_purchase: Optional[PurchaseDetailOut] = None
    documents: List[DocumentOut] = []
    reviews: List[ClaimReviewOut] = []

    model_config = ConfigDict(from_attributes=True)

class ClaimListResponse(BaseModel):
    items: List[ClaimDetailOut]
    total: int
    page: int
    page_size: int

# ----------------- Dashboard & Analytics Schemas -----------------

class ClaimsByStatusStat(BaseModel):
    status: str
    count: int
    total_amount: float

class PoliciesByTypeStat(BaseModel):
    type: str
    count: int
    total_purchases: int

class MonthlyClaimsStat(BaseModel):
    month: str
    submitted_count: int
    approved_count: int
    rejected_count: int
    total_amount: float

class PremiumRevenueStat(BaseModel):
    policy_type: str
    active_policies: int
    total_revenue: float

class DashboardStatsResponse(BaseModel):
    total_users: int
    total_customers: int
    total_agents: int
    total_claims_officers: int
    total_policies: int
    active_policies: int
    total_policy_purchases: int
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    expired_policies: int
    claims_by_status: List[ClaimsByStatusStat]
    policies_by_type: List[PoliciesByTypeStat]
    monthly_claims: List[MonthlyClaimsStat]
    premium_revenue: List[PremiumRevenueStat]

# ----------------- Reports Schemas -----------------

class ClaimReportResponse(BaseModel):
    total_claims: int
    total_claimed_amount: float
    total_approved_amount: float
    claims_by_status: List[ClaimsByStatusStat]
    monthly_trend: List[MonthlyClaimsStat]
    claims_list: List[ClaimDetailOut]

class PolicyReportResponse(BaseModel):
    total_policies: int
    active_policies: int
    inactive_policies: int
    policies_by_type: List[PoliciesByTypeStat]
    popular_policies: List[Dict[str, Any]]

class PremiumReportResponse(BaseModel):
    total_collected_premium: float
    monthly_premium_trend: List[Dict[str, Any]]
    revenue_by_policy_type: List[PremiumRevenueStat]
    top_agents_by_revenue: List[Dict[str, Any]]

# ----------------- Audit Log Schemas -----------------

class AuditLogOut(BaseModel):
    id: int
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None
    action: str
    target_type: str
    target_id: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogListResponse(BaseModel):
    items: List[AuditLogOut]
    total: int
    page: int
    page_size: int

# ----------------- Customer Module Schemas -----------------

class CustomerRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    password: str = Field(..., min_length=6)

class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    password: Optional[str] = Field(None, min_length=6)

class CustomerProfileOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomerPurchaseCreate(BaseModel):
    policy_id: int

class CustomerPurchaseOut(BaseModel):
    id: int
    policy_id: int
    policy_name: str
    policy_number: str
    type: str
    premium: float
    duration_months: int
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime
    claims_count: int = 0

class CustomerPurchaseDetailOut(BaseModel):
    id: int
    policy_id: int
    policy_name: str
    policy_number: str
    type: str
    description: Optional[str] = None
    premium: float
    duration_months: int
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime
    agent_name: Optional[str] = None
    claims: List[Any] = []

class CustomerClaimCreate(BaseModel):
    policy_purchase_id: int
    reason: str = Field(..., min_length=5)
    amount: float = Field(..., gt=0)
    incident_date: Optional[datetime] = None
    description: Optional[str] = None

class CustomerClaimOut(BaseModel):
    id: int
    claim_number: str
    policy_purchase_id: int
    policy_name: str
    policy_number: str
    reason: str
    amount: float
    claim_date: datetime
    status: str
    created_at: datetime
    documents_count: int = 0

class CustomerClaimDetailOut(BaseModel):
    id: int
    claim_number: str
    policy_purchase_id: int
    policy_name: str
    policy_number: str
    policy_type: str
    reason: str
    amount: float
    claim_date: datetime
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    documents: List[DocumentOut] = []
    reviews: List[ClaimReviewOut] = []

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    items: List[NotificationOut]
    unread_count: int
    total: int

class CustomerDashboardResponse(BaseModel):
    customer_name: str
    total_policies: int
    active_policies: int
    expired_policies: int
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    unread_notifications: int
    recent_purchases: List[CustomerPurchaseOut]
    recent_claims: List[CustomerClaimOut]


# ----------------- Claims Officer Module Schemas -----------------

class ClaimReviewCreate(BaseModel):
    decision: str = Field(..., pattern="^(APPROVED|REJECTED|UNDER_REVIEW)$")
    remarks: str = Field(..., min_length=5)


class OfficerClaimOut(BaseModel):
    id: int
    claim_number: str
    policy_purchase_id: int
    policy_name: str
    policy_number: str
    policy_type: str
    reason: str
    amount: float
    claim_date: datetime
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    documents_count: int = 0
    reviews_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class OfficerClaimDetailOut(BaseModel):
    id: int
    claim_number: str
    policy_purchase_id: int
    reason: str
    amount: float
    claim_date: datetime
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    policy_name: Optional[str] = None
    policy_number: Optional[str] = None
    policy_type: Optional[str] = None
    policy_premium: Optional[float] = None
    policy_duration_months: Optional[int] = None
    policy_start_date: Optional[datetime] = None
    policy_end_date: Optional[datetime] = None
    documents: List[DocumentOut] = []
    reviews: List[ClaimReviewOut] = []

    model_config = ConfigDict(from_attributes=True)


class OfficerClaimListResponse(BaseModel):
    items: List[OfficerClaimOut]
    total: int
    page: int
    page_size: int


class OfficerProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    password: Optional[str] = Field(None, min_length=6)


class OfficerProfileOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    reviews_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ClaimsByStatusStat(BaseModel):
    status: str
    count: int
    total_amount: float


class OfficerDashboardResponse(BaseModel):
    officer_name: str
    total_claims: int
    submitted_claims: int
    under_review_claims: int
    approved_claims: int
    rejected_claims: int
    my_reviews_count: int
    pending_review_claims: int
    claims_by_status: List[ClaimsByStatusStat]
    recent_claims: List[OfficerClaimOut]

