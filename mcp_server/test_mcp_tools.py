import pytest
from mcp_tools import (
    get_customer,
    list_customers,
    update_customer,
    create_ticket,
    get_customer_history,
    ToolError,
)


def test_get_customer():
    res = get_customer(1)
    assert isinstance(res, dict)
    assert res["id"] == 1


def test_list_customers():
    res = list_customers(status=None, limit=5)
    assert isinstance(res, list)
    assert len(res) <= 5


def test_update_customer():
    updated = update_customer(1, {"status": "disabled"})
    assert updated["status"] == "disabled"


def test_create_ticket():
    ticket = create_ticket(1, "pytest issue", "high")
    assert ticket["customer_id"] == 1
    assert ticket["issue"] == "pytest issue"


def test_get_customer_history():
    hist = get_customer_history(1)
    assert "customer" in hist
    assert "tickets" in hist
    assert isinstance(hist["tickets"], list)
