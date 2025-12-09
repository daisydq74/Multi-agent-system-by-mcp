
from typing import Any, Dict, Optional

from .data_agent import CustomerDataAgent


class SupportAgent:
    """Agent responsible for generating support responses."""

    name = "support-agent"

    def __init__(self, data_agent: CustomerDataAgent, logger_print=print):
        self.data_agent = data_agent
        self.log = logger_print

    # High-level support logic -----------------------------------------------

    def handle_account_help(self, customer_id: int, query: str) -> Dict[str, Any]:
        """Scenario 1: General account assistance."""
        self.log(f"[{self.name}] Handling account help: id={customer_id}, query={query!r}")

        customer = self.data_agent.fetch_customer(customer_id)
        if "error" in customer:
            return {"reply": customer["error"], "customer": None}

        reply = (
            f"Customer found: {customer['name']} (status: {customer['status']}). "
            f"You said: '{query}'. I can help you with account status, upgrades, "
            "or creating a support ticket."
        )
        return {"reply": reply, "customer": customer}

    def handle_upgrade_request(self, customer_id: int, query: str) -> Dict[str, Any]:
        """Scenario 2: Account upgrade request."""
        self.log(f"[{self.name}] Handling upgrade request: id={customer_id}, query={query!r}")

        customer = self.data_agent.fetch_customer(customer_id)
        if "error" in customer:
            return {"reply": customer["error"]}

        reply = (
            f"Confirmed customer {customer['name']} (ID {customer_id}). "
            "I can create a high-priority ticket for the upgrade request."
        )
        ticket = self.data_agent.open_ticket(
            customer_id, issue="Account upgrade request", priority="high"
        )
        return {"reply": reply, "ticket": ticket}

    def handle_billing_and_cancel(
        self, customer_id: Optional[int], query: str
    ) -> Dict[str, Any]:
        """
        Scenario 2: Multi-intent request: cancellation + billing issue.
        May require additional context from CustomerDataAgent.
        """
        self.log(
            f"[{self.name}] Handling cancel + billing issue: id={customer_id}, query={query!r}"
        )

        if customer_id is None:
            return {
                "needs_context": True,
                "reply": "I need your customer ID to look up billing and cancellation information.",
            }

        customer = self.data_agent.fetch_customer(customer_id)
        if "error" in customer:
            return {"reply": customer["error"]}

        return {
            "needs_billing_context": True,
            "reply": (
                f"Confirmed customer {customer['name']}. "
                "This request involves both cancellation and billing issues. "
                "I need billing history to provide a proper recommendation."
            ),
        }

    def build_refund_response(
        self, customer_id: int, history: Dict[str, Any], query: str
    ) -> Dict[str, Any]:
        """Generates coordinated refund/cancellation response using customer history."""
        self.log(f"[{self.name}] Building refund/escalation response")

        customer = history.get("customer")
        tickets = history.get("tickets", [])

        high_open = [
            t for t in tickets if t["status"] != "resolved" and t["priority"] == "high"
        ]

        reply = (
            f"Customer {customer['name']} (ID {customer_id}) has {len(tickets)} tickets, "
            f"with {len(high_open)} unresolved high-priority issues. "
            "Given your billing message, I recommend:\n"
            "1. Creating a high-priority ticket for the billing + cancellation issue.\n"
            "2. Reviewing charges for potential refunds.\n"
            "3. Pausing further billing until the issue is resolved."
        )

        ticket = self.data_agent.open_ticket(
            customer_id,
            issue="Billing issue + cancellation request",
            priority="high",
        )
        return {"reply": reply, "ticket": ticket, "history_summary": history}

    def report_high_priority_tickets_for_premium(self, customers: list) -> Dict[str, Any]:
        """Scenario 3: Generate report for premium users with high-priority tickets."""
        self.log(f"[{self.name}] Building high-priority ticket report for premium customers")

        rows = []
        for c in customers:
            history = self.data_agent.get_history(c["id"])
            tickets = history.get("tickets", [])
            high = [t for t in tickets if t["priority"] == "high"]
            if not high:
                continue
            rows.append(
                {
                    "customer_id": c["id"],
                    "customer_name": c["name"],
                    "high_priority_tickets": high,
                }
            )

        lines = ["High-Priority Ticket Report (Premium Customers):"]
        for row in rows:
            lines.append(
                f"- {row['customer_name']} (ID {row['customer_id']}): "
                f"{len(row['high_priority_tickets'])} high-priority tickets"
            )

        return {"reply": "\n".join(lines), "rows": rows}
