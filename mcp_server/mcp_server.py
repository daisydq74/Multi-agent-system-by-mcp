# mcp_server.py

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP  # type: ignore

from mcp_tools import (
    get_customer,
    list_customers,
    update_customer,
    create_ticket,
    get_customer_history,
    ToolError,
)

# ---------------------------------------------------------------------------
# Create MCP server instance
# ---------------------------------------------------------------------------
mcp = FastMCP("customer-support-mcp", json_response=True)


# ---------------------------------------------------------------------------
# Tool: get_customer
# ---------------------------------------------------------------------------
@mcp.tool()
def tool_get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single customer by ID.
    Returns:
        dict or None
    """
    try:
        return get_customer(customer_id)
    except ToolError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"internal server error: {e}"}


# ---------------------------------------------------------------------------
# Tool: list_customers
# ---------------------------------------------------------------------------
@mcp.tool()
def tool_list_customers(status: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    List customers with optional status filter.
    """
    try:
        return list_customers(status=status, limit=limit)
    except ToolError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"internal server error: {e}"}


# ---------------------------------------------------------------------------
# Tool: update_customer
# ---------------------------------------------------------------------------
@mcp.tool()
def tool_update_customer(customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update customer fields.
    data may include: name, email, phone, status
    """
    try:
        return update_customer(customer_id, data)
    except ToolError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"internal server error: {e}"}


# ---------------------------------------------------------------------------
# Tool: create_ticket
# ---------------------------------------------------------------------------
@mcp.tool()
def tool_create_ticket(customer_id: int, issue: str, priority: str = "medium") -> Dict[str, Any]:
    """
    Create a support ticket for a customer.
    priority: low / medium / high
    """
    try:
        return create_ticket(customer_id, issue, priority)
    except ToolError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"internal server error: {e}"}


# ---------------------------------------------------------------------------
# Tool: get_customer_history
# ---------------------------------------------------------------------------
@mcp.tool()
def tool_get_customer_history(customer_id: int) -> Dict[str, Any]:
    """
    Return customer info + all tickets (descending order).
    """
    try:
        return get_customer_history(customer_id)
    except ToolError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"internal server error: {e}"}


# ---------------------------------------------------------------------------
# Start server (when executed directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Starting MCP server: customer-support-mcp")
    mcp.run(
)
