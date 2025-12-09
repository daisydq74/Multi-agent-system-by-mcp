

from __future__ import annotations
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

from .data_agent import CustomerDataAgent
from .support_agent import SupportAgent


@dataclass
class RouterResult:
    query: str
    scenario: str
    logs: List[str]
    final_reply: str
    extra: Dict[str, Any]


class RouterAgent:
    name = "router-agent"

    def __init__(self, data_agent: CustomerDataAgent, support_agent: SupportAgent):
        self.data_agent = data_agent
        self.support_agent = support_agent
        self.logs: List[str] = []

    # Logging ----------------------------------------------------------------

    def _log(self, msg: str):
        print(msg)
        self.logs.append(msg)

    def _reset_logs(self):
        self.logs = []

    # Utility ----------------------------------------------------------------

    @staticmethod
    def _extract_customer_id(query: str) -> Optional[int]:
        """Very simple digit extraction."""
        import re
        matches = re.findall(r"\d+", query)
        if not matches:
            return None
        return int(matches[-1])

    # Entry point ------------------------------------------------------------

    def handle_query(self, query: str) -> RouterResult:
        self._reset_logs()
        q = query.lower()

        # Scenario 2: highest priority
        if "cancel" in q and ("billing" in q or "charged" in q):
            return self._scenario_negotiation(query)

        # Scenario 1
        if "customer id" in q:
            return self._scenario_task_allocation(query)

        # Scenario 3
        if ("high priority" in q or "high-priority" in q) and ("premium" in q):
            return self._scenario_multi_step(query)

        return self._scenario_fallback(query)

    # Scenario 1: Task Allocation -------------------------------------------

    def _scenario_task_allocation(self, query: str) -> RouterResult:
        scenario = "task_allocation"
        cid = self._extract_customer_id(query)

        self._log(f"[router] Scenario 1: task allocation → {query!r}")
        self._log(f"[router] Extracted customer_id={cid}")

        if cid is None:
            return RouterResult(query, scenario, self.logs, "Customer ID missing.", extra={})

        self._log(f"[router] → [data-agent]: fetching customer {cid}")
        customer = self.data_agent.fetch_customer(cid)

        if "error" in customer:
            return RouterResult(query, scenario, self.logs, customer["error"], extra={})

        tier = "premium" if customer.get("status") == "active" else "standard"
        self._log(f"[router] Customer tier determined: {tier}")

        self._log(f"[router] → [support-agent]: generate response for {tier} customer")
        result = self.support_agent.handle_account_help(cid, query)

        return RouterResult(query, scenario, self.logs, result["reply"], extra={"customer": customer})

    # Scenario 2: Negotiation / Escalation ----------------------------------

    def _scenario_negotiation(self, query: str) -> RouterResult:
        scenario = "negotiation_escalation"
        cid = self._extract_customer_id(query)

        self._log(f"[router] Scenario 2: negotiation → {query!r}")
        self._log(f"[router] Extracted customer_id={cid}")

        self._log("[router] → [support-agent]: initial evaluation")
        r1 = self.support_agent.handle_billing_and_cancel(cid, query)

        if r1.get("needs_context"):
            return RouterResult(query, scenario, self.logs, r1["reply"], extra={})

        if r1.get("needs_billing_context"):
            self._log("[router] → [data-agent]: fetching customer history")
            history = self.data_agent.get_history(cid)

            self._log("[router] → [support-agent]: build final refund/cancel response")
            r2 = self.support_agent.build_refund_response(cid, history, query)

            final = r1["reply"] + "\n\n" + r2["reply"]
            return RouterResult(query, scenario, self.logs, final, extra={"history": history})

        return RouterResult(query, scenario, self.logs, r1["reply"], extra={})

    # Scenario 3: Multi-step -------------------------------------------------

    def _scenario_multi_step(self, query: str) -> RouterResult:
        scenario = "multi_step_coordination"

        self._log(f"[router] Scenario 3: multi-step coordination → {query!r}")
        self._log("[router] → [data-agent]: fetching premium customers")

        # simple assumption: active = premium
        customers = self.data_agent.fetch_customers(status="active", limit=100)

        self._log("[router] → [support-agent]: generate high-priority ticket report")
        report = self.support_agent.report_high_priority_tickets_for_premium(customers)

        return RouterResult(query, scenario, self.logs, report["reply"], extra=report)

    # Fallback ---------------------------------------------------------------

    def _scenario_fallback(self, query: str) -> RouterResult:
        scenario = "fallback"
        msg = (
            "I could not classify your request into a predefined scenario.\n"
            "Try examples like:\n"
            "- I need help with my account, customer ID 1\n"
            "- I want to cancel my subscription but I'm having billing issues\n"
            "- What's the status of all high-priority tickets for premium customers?\n"
        )
        return RouterResult(query, scenario, self.logs, msg, extra={})
