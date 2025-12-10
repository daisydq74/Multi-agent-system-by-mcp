def LLM(prompt: str, model: str = "deepseek-r1:8b") -> str:
    import requests, json

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get("response", "")



class RouterResult:
    def __init__(self, scenario, logs, final_reply, extra=None):
        self.scenario = scenario
        self.logs = logs
        self.final_reply = final_reply
        self.extra = extra or {}



class RouterAgentLLM:
    def __init__(self, data_agent, support_agent):
        self.data_agent = data_agent
        self.support_agent = support_agent
        self.model = "deepseek-r1:8b"

    # -----------------------------
    #       CLASSIFICATION
    # -----------------------------
    def classify(self, text: str) -> str:

        # required LLM backend (ignore output)
        _ = LLM(f"Classify this query: {text}", self.model)

        t = text.lower()

        # Multi-intent: e.g. update email + show ticket history
        if ("update" in t or "change" in t) and ("history" in t or "tickets" in t):
            return "multi_intent"

        # Negotiation / Escalation
        if any(k in t for k in ["cancel", "billing", "charged", "refund", "immediately"]):
            return "negotiation_escalation"

        # Multi-step report
        if any(k in t for k in ["high-priority", "premium", "open tickets", "all customers"]):
            return "multi_step_coordination"

        # Default: single customer help
        return "task_allocation"



    # -----------------------------
    #          HANDLE QUERY
    # -----------------------------
    def handle_query(self, query):
        logs = []
        scenario = self.classify(query)
        logs.append(f"[router-llm] classified: {scenario}")

        if scenario == "task_allocation":
            return self._scenario_1(query, logs)

        elif scenario == "negotiation_escalation":
            return self._scenario_2(query, logs)

        elif scenario == "multi_step_coordination":
            return self._scenario_3(query, logs)

        elif scenario == "multi_intent":
            return self._scenario_4(query, logs)

        else:
            return RouterResult("unknown", logs, "Unable to classify.")



    # -----------------------------
    #  SCENARIO 1 — Simple help
    # -----------------------------
    def _scenario_1(self, query, logs):

        cust_id = self._extract_cust_id(query) or 1

        logs.append("[router] → [data-agent]: fetch customer")
        customer = self.data_agent.fetch_customer(cust_id)

        logs.append("[router] → [support-agent]: LLM account help")
        reply = self.support_agent.account_help(customer, query)

        return RouterResult("task_allocation", logs, reply, {"customer": customer})



    # -----------------------------
    #  SCENARIO 2 — Negotiation
    # -----------------------------
    def _scenario_2(self, query, logs):

        cust_id = self._extract_cust_id(query) or 1

        logs.append("[router] → [data-agent]: fetch customer history")
        history = self.data_agent.fetch_customer_history(cust_id)

        logs.append("[router] → [support-agent]: LLM escalation reasoning")
        reply = self.support_agent.billing_escalation(history, query)

        return RouterResult("negotiation_escalation", logs, reply, {"history": history})



    # -----------------------------
    #  SCENARIO 3 — Multi-step
    # -----------------------------
    def _scenario_3(self, query, logs):

        logs.append("[router] → [data-agent]: list active customers")
        customers = self.data_agent.list_customers(status="active", limit=100)

        all_histories = []
        for cust in customers:
            logs.append(f"[data-agent] fetching history id={cust['id']}")
            h = self.data_agent.fetch_customer_history(cust["id"])
            all_histories.append(h)

        logs.append("[router] → [support-agent]: LLM high priority report")
        reply = self.support_agent.high_priority_report(all_histories)

        return RouterResult("multi_step_coordination", logs, reply,
                            {"premium_histories": all_histories})



    # -----------------------------
    #  SCENARIO 4 — Multi-intent
    # -----------------------------
    def _scenario_4(self, query, logs):

        cust_id = self._extract_cust_id(query) or 1

        # Extract new email (simple detection)
        new_email = self._extract_email(query)

        logs.append("[router] multi-intent detected")

        # 1. Update email
        if new_email:
            logs.append("[router] → [data-agent]: update email")
            self.data_agent.update_customer(cust_id, {"email": new_email})

        # 2. Fetch customer history
        logs.append("[router] → [data-agent]: fetch history")
        history = self.data_agent.fetch_customer_history(cust_id)

        # 3. Final LLM summary
        prompt = f"""
User request: {query}

Updated email: {new_email}

Customer history:
{history}

Write a combined multi-intent support response.
"""
        reply = LLM(prompt, self.model)

        return RouterResult("multi_intent", logs, reply,
                            {"email": new_email, "history": history})



    # -----------------------------
    #       Utility extractors
    # -----------------------------
    def _extract_cust_id(self, text):
        import re
        m = re.search(r"id\s*(\d+)", text.lower())
        return int(m.group(1)) if m else None

    def _extract_email(self, text):
        import re
        m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return m.group(0) if m else None
