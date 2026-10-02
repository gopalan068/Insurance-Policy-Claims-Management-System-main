import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from seed import seed_database
from models import User, Policy, Claim, PolicyPurchase
from auth import hash_password, verify_password, create_access_token, decode_access_token
from schemas import LoginRequest, PolicyCreate

def test_system():
    print("1. Testing database schema creation and seeding...")
    seed_database()
    db = SessionLocal()

    # Verify admin
    admin = db.query(User).filter(User.email == "admin@insurance.com").first()
    assert admin is not None, "Admin user not found!"
    assert admin.role == "ADMIN", f"Role is {admin.role}, expected ADMIN"
    assert verify_password("Admin@123", admin.password_hash), "Password verification failed!"
    print(f" Admin user verified: {admin.email} (Role: {admin.role})")

    # Verify policies
    policies = db.query(Policy).all()
    assert len(policies) > 0, "No policies found!"
    print(f" Policies count: {len(policies)}")

    # Verify purchases & claims
    purchases = db.query(PolicyPurchase).all()
    claims = db.query(Claim).all()
    print(f" Purchases count: {len(purchases)}, Claims count: {len(claims)}")

    # Verify JWT Token creation and decode
    token = create_access_token({"sub": str(admin.id), "role": admin.role, "email": admin.email})
    payload = decode_access_token(token)
    assert payload is not None, "Failed to decode JWT!"
    assert payload.get("email") == "admin@insurance.com", "JWT payload mismatch!"
    print(" JWT generation and validation passed.")

    db.close()
    print("\n ALL BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_system()
