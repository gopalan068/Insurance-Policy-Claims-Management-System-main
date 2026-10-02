import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database import engine, Base
from seed import seed_database

# Ensure database tables exist and are seeded
Base.metadata.create_all(bind=engine)
seed_database()

client = TestClient(app)

def run_tests():
    print("=" * 70)
    print("RUNNING CUSTOMER MODULE COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    # 1. Registration
    reg_email = "alice.new@example.com"
    reg_payload = {
        "full_name": "Alice Wonderland",
        "email": reg_email,
        "phone": "+1-555-0199",
        "password": "Password@123"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
    alice_token = reg_res.json()["access_token"]
    alice_user = reg_res.json()["user"]
    assert alice_user["role"] == "CUSTOMER"
    print("  [1] Customer Registration: PASSED (Created user Alice Wonderland)")

    # 2. Duplicate email rejection
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 409, f"Duplicate email should return 409, got {dup_res.status_code}"
    print("  [2] Duplicate Email Rejection: PASSED (HTTP 409 Conflict)")

    # 3. Customer Login
    login_res = client.post("/api/auth/login", json={"email": reg_email, "password": "Password@123"})
    assert login_res.status_code == 200
    alice_token = login_res.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    print("  [3] Customer Login: PASSED (Received valid JWT)")

    # 4. Customer Dashboard
    dash_res = client.get("/api/customer/dashboard", headers=alice_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["customer_name"] == "Alice Wonderland"
    assert dash_data["unread_notifications"] >= 1  # Welcome notification
    print("  [4] Customer Dashboard: PASSED (Welcome message, KPIs, unread notification count)")

    # 5. Policy Catalog
    pol_res = client.get("/api/customer/policies", headers=alice_headers)
    assert pol_res.status_code == 200
    policies = pol_res.json()["items"]
    assert len(policies) > 0
    active_policy = policies[0]
    print(f"  [5] Policy Catalog: PASSED ({len(policies)} active policies available)")

    # 6. Policy Details
    pdetail_res = client.get(f"/api/customer/policies/{active_policy['id']}", headers=alice_headers)
    assert pdetail_res.status_code == 200
    assert pdetail_res.json()["name"] == active_policy["name"]
    print("  [6] Policy Details: PASSED")

    # 7. Policy Purchase
    buy_res = client.post(
        "/api/customer/purchases",
        headers=alice_headers,
        json={"policy_id": active_policy["id"]}
    )
    assert buy_res.status_code == 201, f"Purchase failed: {buy_res.text}"
    alice_purchase = buy_res.json()
    assert alice_purchase["status"] == "ACTIVE"
    print(f"  [7] Policy Purchase: PASSED (Subscribed to {alice_purchase['policy_name']}, ID: {alice_purchase['id']})")

    # 8. My Purchases List & Detail
    my_purchases_res = client.get("/api/customer/purchases", headers=alice_headers)
    assert my_purchases_res.status_code == 200
    assert len(my_purchases_res.json()) >= 1
    
    p_detail_res = client.get(f"/api/customer/purchases/{alice_purchase['id']}", headers=alice_headers)
    assert p_detail_res.status_code == 200
    print("  [8] My Purchases & Ownership: PASSED")

    # 9. Claim Submission
    claim_payload = {
        "policy_purchase_id": alice_purchase["id"],
        "reason": "Emergency medical hospitalization and surgery",
        "amount": 2500.00
    }
    claim_res = client.post("/api/customer/claims", headers=alice_headers, json=claim_payload)
    assert claim_res.status_code == 201, f"Claim failed: {claim_res.text}"
    alice_claim = claim_res.json()
    assert alice_claim["status"] == "SUBMITTED"
    assert alice_claim["amount"] == 2500.00
    print(f"  [9] Claim Submission: PASSED (Claim #{alice_claim['claim_number']} created)")

    # 10. Claim Validation (Negative amount rejected)
    bad_claim_res = client.post(
        "/api/customer/claims",
        headers=alice_headers,
        json={"policy_purchase_id": alice_purchase["id"], "reason": "Invalid", "amount": -100}
    )
    assert bad_claim_res.status_code == 422
    print("  [10] Claim Validation: PASSED (Negative amounts rejected with 422)")

    # 11. Document Upload
    dummy_pdf = io.BytesIO(b"%PDF-1.4 Fake Medical Receipt Content\n%%EOF")
    upload_res = client.post(
        f"/api/customer/claims/{alice_claim['id']}/documents",
        headers=alice_headers,
        files={"file": ("hospital_bill.pdf", dummy_pdf, "application/pdf")}
    )
    assert upload_res.status_code == 201, f"Upload failed: {upload_res.text}"
    alice_doc = upload_res.json()
    assert alice_doc["file_name"] == "hospital_bill.pdf"
    print(f"  [11] Document Upload: PASSED (Uploaded {alice_doc['file_name']})")

    # 12. Document Listing
    docs_res = client.get("/api/customer/documents", headers=alice_headers)
    assert docs_res.status_code == 200
    assert len(docs_res.json()) >= 1
    print("  [12] Document Listing: PASSED")

    # 13. Document Download
    doc_file_res = client.get(f"/api/customer/documents/{alice_doc['id']}/file", headers=alice_headers)
    assert doc_file_res.status_code == 200
    print("  [13] Secure Document Download: PASSED")

    # 14. Notifications
    notifs_res = client.get("/api/customer/notifications", headers=alice_headers)
    assert notifs_res.status_code == 200
    notifs_data = notifs_res.json()
    assert notifs_data["total"] >= 3  # Welcome + Purchase + Claim + Document
    first_notif = notifs_data["items"][0]
    print(f"  [14] Notifications: PASSED ({notifs_data['total']} notifications recorded)")

    # 15. Mark Notification Read & Read-All
    read_res = client.patch(f"/api/customer/notifications/{first_notif['id']}/read", headers=alice_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    read_all_res = client.patch("/api/customer/notifications/read-all", headers=alice_headers)
    assert read_all_res.status_code == 200
    print("  [15] Mark Notifications Read: PASSED")

    # 16. Profile Update
    prof_update = client.put(
        "/api/customer/profile",
        headers=alice_headers,
        json={"phone": "+1-555-9999"}
    )
    assert prof_update.status_code == 200
    assert prof_update.json()["phone"] == "+1-555-9999"
    print("  [16] Profile Update: PASSED")

    # 17. Customer -> Admin endpoint (403 Forbidden)
    admin_forbidden = client.get("/api/admin/users", headers=alice_headers)
    assert admin_forbidden.status_code == 403
    print("  [17] RBAC Protection (Customer -> Admin 403): PASSED")

    # 18. Admin -> Customer endpoint (403 Forbidden)
    admin_login = client.post("/api/auth/login", json={"email": "admin@insurance.com", "password": "Admin@123"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    customer_forbidden = client.get("/api/customer/dashboard", headers=admin_headers)
    assert customer_forbidden.status_code == 403
    print("  [18] RBAC Protection (Admin -> Customer 403): PASSED")

    # 19. IDOR Security: Create Customer Bob and test cross-customer isolation
    bob_reg = client.post("/api/auth/register", json={
        "full_name": "Bob Builder",
        "email": "bob.builder@example.com",
        "password": "Password@123"
    })
    assert bob_reg.status_code == 201
    bob_token = bob_reg.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Bob tries to view Alice's purchase -> 404
    bob_view_alice_purchase = client.get(f"/api/customer/purchases/{alice_purchase['id']}", headers=bob_headers)
    assert bob_view_alice_purchase.status_code == 404
    print("  [19] IDOR Protection (Cross-Customer Purchase Access): PASSED (Blocked with 404)")

    # Bob tries to view Alice's claim -> 404
    bob_view_alice_claim = client.get(f"/api/customer/claims/{alice_claim['id']}", headers=bob_headers)
    assert bob_view_alice_claim.status_code == 404
    print("  [20] IDOR Protection (Cross-Customer Claim Access): PASSED (Blocked with 404)")

    # Bob tries to download Alice's document -> 404
    bob_download_alice_doc = client.get(f"/api/customer/documents/{alice_doc['id']}/file", headers=bob_headers)
    assert bob_download_alice_doc.status_code == 404
    print("  [21] IDOR Protection (Cross-Customer Document Download): PASSED (Blocked with 404)")

    print("=" * 70)
    print("ALL 21 CUSTOMER MODULE TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
