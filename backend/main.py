import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import engine, Base
from seed import seed_database

# Routers - Admin
from routers.auth import router as auth_router
from routers.admin_dashboard import router as dashboard_router
from routers.admin_users import router as users_router
from routers.admin_customers import router as customers_router
from routers.admin_agents import router as agents_router
from routers.admin_officers import router as officers_router
from routers.admin_policies import router as policies_router
from routers.admin_purchases import router as purchases_router
from routers.admin_claims import router as claims_router
from routers.admin_documents import router as documents_router
from routers.admin_reports import router as reports_router
from routers.admin_audit import router as audit_router

# Routers - Customer
from routers.customer_dashboard import router as customer_dashboard_router
from routers.customer_policies import router as customer_policies_router
from routers.customer_purchases import router as customer_purchases_router
from routers.customer_claims import router as customer_claims_router
from routers.customer_documents import router as customer_documents_router
from routers.customer_notifications import router as customer_notifications_router
from routers.customer_profile import router as customer_profile_router

# Routers - Claims Officer
from routers.officer_dashboard import router as officer_dashboard_router
from routers.officer_claims import router as officer_claims_router
from routers.officer_reviews import router as officer_reviews_router
from routers.officer_profile import router as officer_profile_router
from routers.officer_notifications import router as officer_notifications_router

# Routers - Agent
from routers.agent_dashboard import router as agent_dashboard_router
from routers.agent_customers import router as agent_customers_router
from routers.agent_purchases import router as agent_purchases_router
from routers.agent_claims import router as agent_claims_router
from routers.agent_profile import router as agent_profile_router
from routers.agent_notifications import router as agent_notifications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo data if database is fresh
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Shutdown logic if any

app = FastAPI(
    title="Insurance Policy & Claims Management System - Unified API",
    description="Unified enterprise backend supporting Admin Management and Customer Portal modules with shared database and RBAC security.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Register Admin & Auth Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(customers_router)
app.include_router(agents_router)
app.include_router(officers_router)
app.include_router(policies_router)
app.include_router(purchases_router)
app.include_router(claims_router)
app.include_router(documents_router)
app.include_router(reports_router)
app.include_router(audit_router)

# Register Customer Routers
app.include_router(customer_dashboard_router)
app.include_router(customer_policies_router)
app.include_router(customer_purchases_router)
app.include_router(customer_claims_router)
app.include_router(customer_documents_router)
app.include_router(customer_notifications_router)
app.include_router(customer_profile_router)

# Register Claims Officer Routers
app.include_router(officer_dashboard_router)
app.include_router(officer_claims_router)
app.include_router(officer_reviews_router)
app.include_router(officer_profile_router)
app.include_router(officer_notifications_router)

# Register Agent Routers
app.include_router(agent_dashboard_router)
app.include_router(agent_customers_router)
app.include_router(agent_purchases_router)
app.include_router(agent_claims_router)
app.include_router(agent_profile_router)
app.include_router(agent_notifications_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Insurance Policy & Claims Management System API",
        "version": "2.0.0",
        "modules": ["Admin Module", "Customer Module", "Claims Officer Module", "Agent Module"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
