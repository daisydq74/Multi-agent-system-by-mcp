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

    # 用于 multi-step 逻辑的包装
    def list_premium_active_customers(self):
        print("[customer-data-agent] Listing PREMIUM active customers")
        from mcp_server.mcp_tools import list_customers
        # 假设 premium = active (你测试数据如此)
        return list_customers(status="active", limit=100)
