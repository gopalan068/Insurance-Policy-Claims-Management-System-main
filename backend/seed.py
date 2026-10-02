import os
from datetime import datetime, timedelta, timezone
from database import engine, SessionLocal, Base
from models import User, Policy, PolicyPurchase, Claim, Document, ClaimReview, AuditLog
from auth import hash_password

def utc_now():
    return datetime.now(timezone.utc)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if Admin already exists
        admin = db.query(User).filter(User.email == "admin@insurance.com").first()
        if not admin:
            admin = User(
                full_name="System Administrator",
                email="admin@insurance.com",
                phone="+1-800-555-0199",
                password_hash=hash_password("Admin@123"),
                role="ADMIN",
                is_active=True,
                created_at=utc_now() - timedelta(days=180)
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("Created default admin: admin@insurance.com")

        # Seed Customers if empty
        customer_count = db.query(User).filter(User.role == "CUSTOMER").count()
        if customer_count == 0:
            customers = [
                User(
                    full_name="Johnathan Vance",
                    email="john.vance@example.com",
                    phone="+1-555-0101",
                    password_hash=hash_password("Customer@123"),
                    role="CUSTOMER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=120)
                ),
                User(
                    full_name="Sarah Jenkins",
                    email="sarah.j@example.com",
                    phone="+1-555-0102",
                    password_hash=hash_password("Customer@123"),
                    role="CUSTOMER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=90)
                ),
                User(
                    full_name="David Miller",
                    email="david.miller@example.com",
                    phone="+1-555-0103",
                    password_hash=hash_password("Customer@123"),
                    role="CUSTOMER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=60)
                ),
                User(
                    full_name="Emily Watson",
                    email="emily.w@example.com",
                    phone="+1-555-0104",
                    password_hash=hash_password("Customer@123"),
                    role="CUSTOMER",
                    is_active=False,  # Inactive customer for testing filters
                    created_at=utc_now() - timedelta(days=45)
                ),
                User(
                    full_name="Michael Chang",
                    email="michael.c@example.com",
                    phone="+1-555-0105",
                    password_hash=hash_password("Customer@123"),
                    role="CUSTOMER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=30)
                ),
            ]
            db.add_all(customers)
            db.commit()
            print("Seeded sample customers")

        # Seed Agents if empty
        agent_count = db.query(User).filter(User.role == "AGENT").count()
        if agent_count == 0:
            agents = [
                User(
                    full_name="Robert Sterling",
                    email="robert.agent@insurance.com",
                    phone="+1-555-0201",
                    password_hash=hash_password("Agent@123"),
                    role="AGENT",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=150)
                ),
                User(
                    full_name="Elena Rodriguez",
                    email="elena.agent@insurance.com",
                    phone="+1-555-0202",
                    password_hash=hash_password("Agent@123"),
                    role="AGENT",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=100)
                ),
                User(
                    full_name="Marcus Brody",
                    email="marcus.agent@insurance.com",
                    phone="+1-555-0203",
                    password_hash=hash_password("Agent@123"),
                    role="AGENT",
                    is_active=False,
                    created_at=utc_now() - timedelta(days=80)
                )
            ]
            db.add_all(agents)
            db.commit()
            print("Seeded sample agents")

        # Seed Claims Officers if empty
        officer_count = db.query(User).filter(User.role == "CLAIMS_OFFICER").count()
        if officer_count == 0:
            officers = [
                User(
                    full_name="Captain Frank Morrison",
                    email="frank.officer@insurance.com",
                    phone="+1-555-0301",
                    password_hash=hash_password("Officer@123"),
                    role="CLAIMS_OFFICER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=160)
                ),
                User(
                    full_name="Diana Prince",
                    email="diana.officer@insurance.com",
                    phone="+1-555-0302",
                    password_hash=hash_password("Officer@123"),
                    role="CLAIMS_OFFICER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=110)
                ),
                User(
                    full_name="Arthur Pendelton",
                    email="arthur.officer@insurance.com",
                    phone="+1-555-0303",
                    password_hash=hash_password("Officer@123"),
                    role="CLAIMS_OFFICER",
                    is_active=True,
                    created_at=utc_now() - timedelta(days=70)
                )
            ]
            db.add_all(officers)
            db.commit()
            print("Seeded sample claims officers")

        # Seed Policies if empty
        policy_count = db.query(Policy).count()
        if policy_count == 0:
            policies = [
                Policy(
                    policy_number="POL-HLTH-101",
                    name="Apex Comprehensive Health Plan",
                    type="HEALTH",
                    description="Full medical hospitalization, emergency ambulance, and critical illness cover with zero copay.",
                    premium=450.00,
                    duration_months=12,
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=140)
                ),
                Policy(
                    policy_number="POL-LIFE-201",
                    name="Horizon Term Life Shield",
                    type="LIFE",
                    description="Pure term life protection offering up to $1,000,000 lump-sum death benefit payout for dependents.",
                    premium=650.00,
                    duration_months=24,
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=130)
                ),
                Policy(
                    policy_number="POL-AUTO-301",
                    name="Titan Auto Comprehensive",
                    type="VEHICLE",
                    description="Collision, theft, third-party liability, and 24/7 roadside assistance cover for personal motor vehicles.",
                    premium=320.00,
                    duration_months=12,
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=110)
                ),
                Policy(
                    policy_number="POL-TRV-401",
                    name="Global Voyager Travel Guard",
                    type="TRAVEL",
                    description="International travel cancellation, lost baggage, passport loss, and emergency overseas medical care.",
                    premium=120.00,
                    duration_months=6,
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=100)
                ),
                Policy(
                    policy_number="POL-HOME-501",
                    name="Sanctuary Home & Property Safe",
                    type="HOME",
                    description="Structural damage, fire, burglary, flood protection, and temporary living expense reimbursement.",
                    premium=550.00,
                    duration_months=12,
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=90)
                ),
                Policy(
                    policy_number="POL-HLTH-102",
                    name="Senior WellCare Elite",
                    type="HEALTH",
                    description="Specialized elder healthcare cover including OPD visits, prescription refills, and physiotherapy.",
                    premium=780.00,
                    duration_months=12,
                    status="INACTIVE",
                    created_at=utc_now() - timedelta(days=80)
                ),
            ]
            db.add_all(policies)
            db.commit()
            print("Seeded sample policies")

        # Seed Policy Purchases if empty
        purchase_count = db.query(PolicyPurchase).count()
        if purchase_count == 0:
            cust1 = db.query(User).filter(User.email == "john.vance@example.com").first()
            cust2 = db.query(User).filter(User.email == "sarah.j@example.com").first()
            cust3 = db.query(User).filter(User.email == "david.miller@example.com").first()
            cust5 = db.query(User).filter(User.email == "michael.c@example.com").first()

            agent1 = db.query(User).filter(User.email == "robert.agent@insurance.com").first()
            agent2 = db.query(User).filter(User.email == "elena.agent@insurance.com").first()

            p_hlth = db.query(Policy).filter(Policy.policy_number == "POL-HLTH-101").first()
            p_life = db.query(Policy).filter(Policy.policy_number == "POL-LIFE-201").first()
            p_auto = db.query(Policy).filter(Policy.policy_number == "POL-AUTO-301").first()
            p_trv = db.query(Policy).filter(Policy.policy_number == "POL-TRV-401").first()
            p_home = db.query(Policy).filter(Policy.policy_number == "POL-HOME-501").first()

            purchases = [
                PolicyPurchase(
                    policy_id=p_hlth.id,
                    customer_id=cust1.id,
                    agent_id=agent1.id,
                    start_date=utc_now() - timedelta(days=100),
                    end_date=utc_now() + timedelta(days=265),
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=100)
                ),
                PolicyPurchase(
                    policy_id=p_auto.id,
                    customer_id=cust1.id,
                    agent_id=agent2.id,
                    start_date=utc_now() - timedelta(days=80),
                    end_date=utc_now() + timedelta(days=285),
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=80)
                ),
                PolicyPurchase(
                    policy_id=p_life.id,
                    customer_id=cust2.id,
                    agent_id=agent1.id,
                    start_date=utc_now() - timedelta(days=90),
                    end_date=utc_now() + timedelta(days=640),
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=90)
                ),
                PolicyPurchase(
                    policy_id=p_trv.id,
                    customer_id=cust3.id,
                    agent_id=agent2.id,
                    start_date=utc_now() - timedelta(days=120),
                    end_date=utc_now() - timedelta(days=30),
                    status="EXPIRED",
                    created_at=utc_now() - timedelta(days=120)
                ),
                PolicyPurchase(
                    policy_id=p_home.id,
                    customer_id=cust5.id,
                    agent_id=agent1.id,
                    start_date=utc_now() - timedelta(days=30),
                    end_date=utc_now() + timedelta(days=335),
                    status="ACTIVE",
                    created_at=utc_now() - timedelta(days=30)
                ),
            ]
            db.add_all(purchases)
            db.commit()
            print("Seeded sample policy purchases")

        # Seed Claims if empty
        claim_count = db.query(Claim).count()
        if claim_count == 0:
            purchases = db.query(PolicyPurchase).all()
            officer1 = db.query(User).filter(User.email == "frank.officer@insurance.com").first()
            officer2 = db.query(User).filter(User.email == "diana.officer@insurance.com").first()

            # Ensure upload folder has sample mock files
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            sample_file_path = os.path.join(upload_dir, "sample_claim_document.pdf")
            if not os.path.exists(sample_file_path):
                with open(sample_file_path, "w") as f:
                    f.write("%PDF-1.4 Mock Insurance Claim Supporting Document\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n0\n%%EOF")

            c1 = Claim(
                claim_number="CLM-2026-001",
                policy_purchase_id=purchases[0].id,
                customer_id=purchases[0].customer_id,
                reason="Emergency Appendectomy surgery and 3-day post-op hospital stay at Metro General.",
                amount=3850.00,
                claim_date=utc_now() - timedelta(days=40),
                status="APPROVED",
                created_at=utc_now() - timedelta(days=40)
            )
            c2 = Claim(
                claim_number="CLM-2026-002",
                policy_purchase_id=purchases[1].id,
                customer_id=purchases[1].customer_id,
                reason="Rear bumper and trunk collision damage sustained in highway traffic incident.",
                amount=1420.00,
                claim_date=utc_now() - timedelta(days=20),
                status="UNDER_REVIEW",
                created_at=utc_now() - timedelta(days=20)
            )
            c3 = Claim(
                claim_number="CLM-2026-003",
                policy_purchase_id=purchases[2].id,
                customer_id=purchases[2].customer_id,
                reason="Critical illness hospitalization diagnostic screening charges.",
                amount=2100.00,
                claim_date=utc_now() - timedelta(days=5),
                status="SUBMITTED",
                created_at=utc_now() - timedelta(days=5)
            )
            c4 = Claim(
                claim_number="CLM-2026-004",
                policy_purchase_id=purchases[3].id,
                customer_id=purchases[3].customer_id,
                reason="Flight baggage loss claim filed after policy expiration date.",
                amount=890.00,
                claim_date=utc_now() - timedelta(days=15),
                status="REJECTED",
                created_at=utc_now() - timedelta(days=15)
            )

            db.add_all([c1, c2, c3, c4])
            db.commit()

            # Seed Documents
            doc1 = Document(
                claim_id=c1.id,
                file_name="Hospital_Discharge_Summary_Invoice.pdf",
                file_path="uploads/sample_claim_document.pdf",
                file_type="application/pdf",
                uploaded_date=utc_now() - timedelta(days=40)
            )
            doc2 = Document(
                claim_id=c1.id,
                file_name="Surgeon_Consultation_Prescription.pdf",
                file_path="uploads/sample_claim_document.pdf",
                file_type="application/pdf",
                uploaded_date=utc_now() - timedelta(days=40)
            )
            doc3 = Document(
                claim_id=c2.id,
                file_name="Police_Incident_Report_FIR.pdf",
                file_path="uploads/sample_claim_document.pdf",
                file_type="application/pdf",
                uploaded_date=utc_now() - timedelta(days=20)
            )
            doc4 = Document(
                claim_id=c2.id,
                file_name="BodyShop_Repair_Estimate.pdf",
                file_path="uploads/sample_claim_document.pdf",
                file_type="application/pdf",
                uploaded_date=utc_now() - timedelta(days=19)
            )
            doc5 = Document(
                claim_id=c3.id,
                file_name="Pathology_Lab_Results.pdf",
                file_path="uploads/sample_claim_document.pdf",
                file_type="application/pdf",
                uploaded_date=utc_now() - timedelta(days=5)
            )
            doc6 = Document(
                claim_id=c4.id,
                file_name="Airline_PIR_Receipt.pdf",
                file_path="uploads/sample_claim_document.pdf",
                file_type="application/pdf",
                uploaded_date=utc_now() - timedelta(days=15)
            )
            db.add_all([doc1, doc2, doc3, doc4, doc5, doc6])
            db.commit()

            # Seed Claim Reviews
            rev1 = ClaimReview(
                claim_id=c1.id,
                officer_id=officer1.id,
                decision="APPROVED",
                remarks="All medical discharge summaries, receipts, and hospital accreditations verified. Approved for full reimbursement settlement.",
                review_date=utc_now() - timedelta(days=35)
            )
            rev2 = ClaimReview(
                claim_id=c2.id,
                officer_id=officer2.id,
                decision="UNDER_REVIEW",
                remarks="Police accident report reviewed. Awaiting secondary independent surveyor assessment on bodywork pricing.",
                review_date=utc_now() - timedelta(days=10)
            )
            rev3 = ClaimReview(
                claim_id=c4.id,
                officer_id=officer1.id,
                decision="REJECTED",
                remarks="Incident occurred post policy expiration period. Clause 4.2 of travel insurance policy precludes coverage.",
                review_date=utc_now() - timedelta(days=12)
            )
            db.add_all([rev1, rev2, rev3])
            db.commit()
            print("Seeded sample claims, documents, and reviews")

        # Seed initial audit logs if empty
        if db.query(AuditLog).count() == 0 and admin:
            logs = [
                AuditLog(
                    admin_id=admin.id,
                    action="SYSTEM_INIT",
                    target_type="SYSTEM",
                    target_id="0",
                    details="Insurance Management System initialized with production schema.",
                    timestamp=utc_now() - timedelta(days=180)
                ),
                AuditLog(
                    admin_id=admin.id,
                    action="CREATE_POLICY",
                    target_type="POLICY",
                    target_id="POL-HLTH-101",
                    details="Created Apex Comprehensive Health Plan.",
                    timestamp=utc_now() - timedelta(days=140)
                ),
                AuditLog(
                    admin_id=admin.id,
                    action="ACTIVATE_AGENT",
                    target_type="USER",
                    target_id="Robert Sterling",
                    details="Activated agent profile robert.agent@insurance.com.",
                    timestamp=utc_now() - timedelta(days=120)
                )
            ]
            db.add_all(logs)
            db.commit()
            print("Seeded initial audit logs")

    except Exception as e:
        db.rollback()
        print(f"Error during database seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
