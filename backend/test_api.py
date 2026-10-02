import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoints():
    print("Testing API endpoints...")

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(" Health check passed: 200 OK")

    # 2. Login invalid
    res = client.post("/api/auth/login", json={"email": "wrong@insurance.com", "password": "WrongPassword"})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    print(" Invalid login rejected: 401 Unauthorized")

    # 3. Admin login
    res = client.post("/api/auth/login", json={"email": "admin@insurance.com", "password": "Admin@123"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    data = res.json()
    token = data["access_token"]
    assert token is not None
    assert data["user"]["role"] == "ADMIN"
    print(f" Admin login successful: token received for {data['user']['email']}")

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Customer login (should get token, but be rejected by admin endpoints)
    cust_res = client.post("/api/auth/login", json={"email": "john.vance@example.com", "password": "Customer@123"})
    assert cust_res.status_code == 200
    cust_token = cust_res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 5. Test RBAC: Customer trying to access Admin dashboard -> 403 Forbidden
    rbac_res = client.get("/api/admin/dashboard", headers=cust_headers)
    assert rbac_res.status_code == 403, f"Expected 403 for Customer on Admin API, got {rbac_res.status_code}"
    print(" RBAC verified: Customer denied access to Admin Dashboard (403 Forbidden)")

    # 6. Admin Dashboard Stats
    dash_res = client.get("/api/admin/dashboard", headers=headers)
    assert dash_res.status_code == 200, f"Dashboard failed: {dash_res.text}"
    dash_data = dash_res.json()
    assert dash_data["total_users"] > 0
    assert dash_data["total_policies"] > 0
    assert len(dash_data["claims_by_status"]) > 0
    assert len(dash_data["policies_by_type"]) > 0
    print(f" Dashboard stats verified: {dash_data['total_users']} users, {dash_data['total_policies']} policies, {dash_data['total_claims']} claims")

    # 7. Admin Users List & Filter
    users_res = client.get("/api/admin/users?role=AGENT", headers=headers)
    assert users_res.status_code == 200
    assert len(users_res.json()["items"]) > 0
    print(f" Users API verified: {users_res.json()['total']} agents listed")

    # 8. Admin Policies List & Search
    pol_res = client.get("/api/admin/policies?type=HEALTH", headers=headers)
    assert pol_res.status_code == 200
    assert len(pol_res.json()["items"]) > 0
    print(f" Policies API verified: {pol_res.json()['total']} health policies listed")

    # 9. Admin Policy Purchases
    purch_res = client.get("/api/admin/policy-purchases", headers=headers)
    assert purch_res.status_code == 200
    assert len(purch_res.json()["items"]) > 0
    print(f" Purchases API verified: {purch_res.json()['total']} purchases listed")

    # 10. Admin Claims Monitoring & Details
    claims_res = client.get("/api/admin/claims", headers=headers)
    assert claims_res.status_code == 200
    claim_items = claims_res.json()["items"]
    assert len(claim_items) > 0
    c_id = claim_items[0]["id"]
    claim_det = client.get(f"/api/admin/claims/{c_id}", headers=headers)
    assert claim_det.status_code == 200
    assert "documents" in claim_det.json()
    assert "reviews" in claim_det.json()
    print(f" Claims API & Claim Details verified: Claim #{claim_items[0]['claim_number']} with {len(claim_det.json()['documents'])} docs and {len(claim_det.json()['reviews'])} reviews")

    # 11. Admin Reports
    rep_claims = client.get("/api/admin/reports/claims", headers=headers)
    assert rep_claims.status_code == 200
    rep_pols = client.get("/api/admin/reports/policies", headers=headers)
    assert rep_pols.status_code == 200
    rep_prem = client.get("/api/admin/reports/premium", headers=headers)
    assert rep_prem.status_code == 200
    print(" All 3 Reports endpoints verified: claims, policies, premium")

    # 12. Admin Audit Logs
    audit_res = client.get("/api/admin/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    assert len(audit_res.json()["items"]) > 0
    print(f" Audit Logs API verified: {audit_res.json()['total']} logs listed")

    print("\n ALL API INTEGRATION TESTS PASSED 100%!")

if __name__ == "__main__":
    test_endpoints()
