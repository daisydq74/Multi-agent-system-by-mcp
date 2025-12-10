# agents/data_agent.py



class CustomerDataAgent:
    def fetch_customer(self, cid):
        print(f"[customer-data-agent] Fetching customer: id={cid}")
        from mcp_server.mcp_tools import get_customer
        return get_customer(cid)

    def fetch_customer_history(self, cid):
        print(f"[customer-data-agent] Fetching customer history: id={cid}")
        from mcp_server.mcp_tools import get_customer_history
        return get_customer_history(cid)


    def list_customers(self, status=None, limit=100):
        print(f"[customer-data-agent] Listing customers: status={status}, limit={limit}")
        from mcp_server.mcp_tools import list_customers
        return list_customers(status=status, limit=limit)

    #  multi-step
    def list_premium_active_customers(self):
        print("[customer-data-agent] Listing PREMIUM active customers")
        from mcp_server.mcp_tools import list_customers
        return list_customers(status="active", limit=100)

    def update_customer(self, customer_id: int, data: dict) -> dict:
        """
        Update customer partial data, e.g. {"email": "..."}.
        """
        from mcp_server.mcp_tools import update_customer
        print(f"[customer-data-agent] Updating customer {customer_id}: {data}")
        return update_customer(customer_id, data)

    # -----------------------------
    # Create ticket
    # -----------------------------
    def create_ticket(self, customer_id: int, issue: str, priority="medium") -> dict:
        from mcp_server.mcp_tools import  create_ticket
        print(f"[customer-data-agent] Creating ticket for {customer_id}: {issue}")
        return create_ticket(customer_id, issue, priority)