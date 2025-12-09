from typing import Any, Dict, List, Optional

from mcp_server.mcp_tools import (
    get_customer,
    list_customers,
    update_customer,
    create_ticket,
    get_customer_history,
    ToolError,
)


class CustomerDataAgent:
    """Agent responsible for customer and ticket data operations."""

    name = "customer-data-agent"

    def __init__(self, logger_print=print):
        self.log = logger_print

    # Basic wrappers ---------------------------------------------------------

    def fetch_customer(self, customer_id: int) -> Dict[str, Any]:
        self.log(f"[{self.name}] Fetching customer: id={customer_id}")
        try:
            customer = get_customer(customer_id)
            if not customer:
                return {"error": f"Customer {customer_id} not found."}
            return customer
        except ToolError as e:
            return {"error": str(e)}

    def fetch_customers(
        self, status: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        self.log(f"[{self.name}] Listing customers: status={status}, limit={limit}")
        try:
            return list_customers(status=status, limit=limit)
        except ToolError as e:
            return [{"error": str(e)}]

    def update_customer_fields(
        self, customer_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        self.log(f"[{self.name}] Updating customer {customer_id}: {data}")
        try:
            return update_customer(customer_id, data)
        except ToolError as e:
            return {"error": str(e)}

    def open_ticket(
        self, customer_id: int, issue: str, priority: str = "medium"
    ) -> Dict[str, Any]:
        self.log(
            f"[{self.name}] Creating ticket: customer_id={customer_id}, "
            f"priority={priority}, issue={issue!r}"
        )
        try:
            return create_ticket(customer_id, issue, priority)
        except ToolError as e:
            return {"error": str(e)}

    def get_history(self, customer_id: int) -> Dict[str, Any]:
        self.log(f"[{self.name}] Fetching customer history: id={customer_id}")
        try:
            return get_customer_history(customer_id)
        except ToolError as e:
            return {"error": str(e)}
