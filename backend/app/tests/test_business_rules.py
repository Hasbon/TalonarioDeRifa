"""Pruebas obligatorias de reglas de negocio de la rifa digital."""

from datetime import date

from app.tests.conftest import auth
from app.utils.winner import derive_winner_code


def test_100_numbers_created_with_leading_zeros(client):
    r = client.get("/api/public/tickets")
    assert r.status_code == 200
    tickets = r.json()
    assert len(tickets) == 100
    codes = [t["number_code"] for t in tickets]
    assert codes[0] == "00"
    assert codes[7] == "07"
    assert codes[99] == "99"
    assert all(len(c) == 2 for c in codes)


def test_initial_ticket_price_30000(client):
    r = client.get("/api/public/raffle")
    assert r.status_code == 200
    assert r.json()["ticket_price"] == 30000
    assert r.json()["draw_date"] == "2026-12-30"


def test_assignment_without_full_payment_stays_active(client, seller_token):
    r = client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Juan Pérez",
            "customer_phone": "3001234567",
            "number_code": "27",
            "initial_payment": 10000,
            "payment_due_date": "2026-12-20",
        },
    )
    assert r.status_code == 201, r.text
    sale = r.json()
    assert sale["commercial_status"] == "active"
    assert sale["payment_status"] == "partial"
    assert sale["balance_due"] == 20000
    assert sale["number_code"] == "27"

    pub = client.get("/api/public/tickets/27")
    assert pub.json()["available"] is False


def test_no_auto_release_on_overdue(client, seller_token):
    r = client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Ana López",
            "customer_phone": "3009998877",
            "number_code": "15",
            "initial_payment": 0,
            "payment_due_date": "2020-01-01",
        },
    )
    assert r.status_code == 201
    pub = client.get("/api/public/tickets/15")
    assert pub.json()["available"] is False
    # Still active despite overdue commitment date
    sales = client.get("/api/sales", headers=auth(seller_token)).json()
    sale = next(s for s in sales if s["number_code"] == "15")
    assert sale["commercial_status"] == "active"
    assert sale["payment_due_date"] == "2020-01-01"
    assert date.fromisoformat(sale["payment_due_date"]) < date.today()


def test_cancel_releases_without_deleting_history(client, seller_token, admin_token):
    r = client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Carlos Ruiz",
            "customer_phone": "3011112233",
            "number_code": "42",
            "initial_payment": 5000,
        },
    )
    sale_id = r.json()["id"]
    token = r.json()["public_token"]

    cancel = client.post(
        f"/api/sales/{sale_id}/cancel",
        headers=auth(admin_token),
        json={"reason": "Cliente desistió del número"},
    )
    assert cancel.status_code == 200
    assert cancel.json()["commercial_status"] == "cancelled"
    assert len(cancel.json()["payments"]) == 1

    pub = client.get("/api/public/tickets/42")
    assert pub.json()["available"] is True

    boleta = client.get(f"/api/public/boletas/{token}")
    assert boleta.json()["validity"] == "revoked"
    assert boleta.json()["assignment_status"] == "cancelled"


def test_cannot_create_two_active_assignments(client, seller_token):
    body = {
        "customer_full_name": "Cliente A",
        "customer_phone": "3020000001",
        "number_code": "07",
        "initial_payment": 0,
    }
    r1 = client.post("/api/sales", headers=auth(seller_token), json=body)
    assert r1.status_code == 201
    body2 = {**body, "customer_phone": "3020000002", "customer_full_name": "Cliente B"}
    r2 = client.post("/api/sales", headers=auth(seller_token), json=body2)
    assert r2.status_code == 409


def test_concurrent_assignments_no_duplicates(client, seller_token):
    """Simulate rapid competing assignments to the same number.

    True multi-connection concurrency is validated against PostgreSQL
    (partial unique index). Here we verify sequential races still yield
    exactly one active assignment and 409 on the rest.
    """
    results = []
    for i in range(5):
        results.append(
            client.post(
                "/api/sales",
                headers=auth(seller_token),
                json={
                    "customer_full_name": f"Concurrente {i}",
                    "customer_phone": f"310000{i:04d}",
                    "number_code": "88",
                    "initial_payment": 0,
                },
            )
        )

    successes = [r for r in results if r.status_code == 201]
    conflicts = [r for r in results if r.status_code == 409]
    assert len(successes) == 1
    assert len(conflicts) == 4
    pub = client.get("/api/public/tickets/88").json()
    assert pub["available"] is False


def test_payments_sum_and_balance(client, seller_token):
    r = client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Pago Test",
            "customer_phone": "3155556677",
            "number_code": "33",
            "initial_payment": 10000,
        },
    )
    sale_id = r.json()["id"]
    p2 = client.post(
        f"/api/sales/{sale_id}/payments",
        headers=auth(seller_token),
        json={"amount": 10000, "payment_method": "transferencia"},
    )
    assert p2.status_code == 201
    sale = client.get(f"/api/sales/{sale_id}", headers=auth(seller_token)).json()
    assert sale["total_paid"] == 20000
    assert sale["balance_due"] == 10000
    assert sale["payment_status"] == "partial"

    client.post(
        f"/api/sales/{sale_id}/payments",
        headers=auth(seller_token),
        json={"amount": 10000, "payment_method": "efectivo"},
    )
    sale = client.get(f"/api/sales/{sale_id}", headers=auth(seller_token)).json()
    assert sale["balance_due"] == 0
    assert sale["payment_status"] == "paid"


def test_voided_payments_not_counted(client, seller_token, admin_token):
    r = client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Void Test",
            "customer_phone": "3166667788",
            "number_code": "44",
            "initial_payment": 20000,
        },
    )
    sale_id = r.json()["id"]
    pay_id = r.json()["payments"][0]["id"]
    void = client.post(f"/api/payments/{pay_id}/void", headers=auth(admin_token))
    assert void.status_code == 200
    sale = client.get(f"/api/sales/{sale_id}", headers=auth(seller_token)).json()
    assert sale["total_paid"] == 0
    assert sale["balance_due"] == 30000


def test_seller_cannot_admin_actions(client, seller_token):
    r = client.get("/api/admin/users", headers=auth(seller_token))
    assert r.status_code == 403
    r2 = client.post(
        "/api/admin/raffle/results",
        headers=auth(seller_token),
        json={
            "lottery_name": "Lotería del Valle",
            "draw_reference": "test",
            "draw_date": "2026-12-30",
            "winning_number": "12347",
            "official_source_url": "https://example.com",
        },
    )
    assert r2.status_code == 403


def test_public_hides_private_data(client, seller_token):
    client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Privado Nombre",
            "customer_phone": "3177778899",
            "number_code": "55",
            "initial_payment": 5000,
        },
    )
    tickets = client.get("/api/public/tickets").json()
    occupied = next(t for t in tickets if t["number_code"] == "55")
    assert occupied["available"] is False
    assert "customer" not in occupied
    assert "phone" not in occupied
    detail = client.get("/api/public/tickets/55").json()
    assert "phone" not in detail
    assert "Privado" not in str(detail)


def test_qr_token_validation(client, seller_token):
    r = client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "QR Cliente",
            "customer_phone": "3188889900",
            "number_code": "66",
            "initial_payment": 30000,
        },
    )
    token = r.json()["public_token"]
    assert token and len(token) > 20
    boleta = client.get(f"/api/public/boletas/{token}").json()
    assert boleta["number_code"] == "66"
    assert boleta["validity"] == "valid"
    assert "phone" not in boleta
    assert boleta.get("financial_label") == "Pagada"


def test_winner_derivation_and_confirm(client, admin_token):
    assert derive_winner_code("12347") == "47"
    try:
        derive_winner_code("9")
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert derive_winner_code("07") == "07"

    create = client.post(
        "/api/admin/raffle/results",
        headers=auth(admin_token),
        json={
            "lottery_name": "Lotería del Valle",
            "draw_reference": "Sorteo 30-dic-2026",
            "draw_date": "2026-12-30",
            "winning_number": "458147",
            "official_source_url": "https://example.com/oficial",
        },
    )
    assert create.status_code == 201
    assert create.json()["derived_winner_code"] == "47"
    assert create.json()["verification_status"] == "draft"
    result_id = create.json()["id"]

    # Public visitors must not confirm
    # Seller cannot either — already tested. Confirm as admin:
    conf = client.post(
        f"/api/admin/raffle/results/{result_id}/confirm",
        headers=auth(admin_token),
    )
    assert conf.status_code == 200
    assert conf.json()["verification_status"] == "confirmed"
    # Unassigned winner number yields clear flag
    assert conf.json()["has_active_assignment"] is False


def test_reports_match_db(client, seller_token, admin_token):
    client.post(
        "/api/sales",
        headers=auth(seller_token),
        json={
            "customer_full_name": "Reporte",
            "customer_phone": "3199990011",
            "number_code": "11",
            "initial_payment": 10000,
        },
    )
    stats = client.get("/api/admin/reports", headers=auth(admin_token)).json()
    assert stats["total_numbers"] == 100
    assert stats["assigned"] >= 1
    assert stats["available"] == stats["total_numbers"] - stats["assigned"]
    assert stats["total_received"] >= 10000
    assert stats["total_outstanding"] >= 20000


def test_draw_dates_remain_2026(client):
    raffle = client.get("/api/public/raffle").json()
    assert raffle["draw_date"].startswith("2026")
    assert "2026-12-31" in raffle["delivery_datetime"]
