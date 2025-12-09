import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_FILENAME = "../support.db"


class ToolError(Exception):
    """Custom exception for tool-level errors."""
    pass


def _db_path() -> Path:
    base = Path(__file__).resolve().parent
    return base / DB_FILENAME



def _connect() -> sqlite3.Connection:
    """
    Open a new database connection.
    """
    path = _db_path()
    if not path.exists():
        raise ToolError(f"Database file not found: {path}")

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _fetch_one(query: str, params: Tuple[Any, ...]) -> Optional[Dict[str, Any]]:
    """Internal helper to run a SELECT that returns a single row."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        if row is None:
            return None
        return dict(row)


def _fetch_all(query: str, params: Tuple[Any, ...]) -> List[Dict[str, Any]]:
    """Internal helper to run a SELECT that returns multiple rows."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]




def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """
    Return a single customer record by ID.
    """
    sql = """
        SELECT id, name, email, phone, status,
               created_at, updated_at
        FROM customers
        WHERE id = ?
    """
    return _fetch_one(sql, (customer_id,))


def list_customers(status: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    List customers, optionally filtered by status ("active" / "disabled").
    """
    if limit <= 0:
        limit = 20  # sane default

    if status:
        sql = """
            SELECT id, name, email, phone, status,
                   created_at, updated_at
            FROM customers
            WHERE status = ?
            ORDER BY id
            LIMIT ?
        """
        params: Tuple[Any, ...] = (status, limit)
    else:
        sql = """
            SELECT id, name, email, phone, status,
                   created_at, updated_at
            FROM customers
            ORDER BY id
            LIMIT ?
        """
        params = (limit,)

    return _fetch_all(sql, params)


def update_customer(customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update fields on a customer record.
    """
    if not data:
        raise ToolError("No fields provided for update.")

    allowed_fields = {"name", "email", "phone", "status"}
    fields = [f for f in data.keys() if f in allowed_fields]

    if not fields:
        raise ToolError(f"No valid fields in update payload: {list(data.keys())}")

    set_clause = ", ".join(f"{f} = ?" for f in fields)
    values = [data[f] for f in fields]
    values.append(customer_id)

    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE customers SET {set_clause} WHERE id = ?", values)
        conn.commit()

        if cur.rowcount == 0:
            raise ToolError(f"Customer {customer_id} not found or not modified.")

        # Return the fresh version from the DB
        cur.execute(
            """
            SELECT id, name, email, phone, status,
                   created_at, updated_at
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        )
        row = cur.fetchone()
        if row is None:
            # This really shouldn't happen if rowcount > 0, but be defensive.
            raise ToolError(f"Customer {customer_id} disappeared after update.")

        return dict(row)


def create_ticket(customer_id: int, issue: str, priority: str = "medium") -> Dict[str, Any]:
    """
    Create a new ticket for the given customer.
    """
    if not issue.strip():
        raise ToolError("Ticket issue cannot be empty.")

    if priority not in ("low", "medium", "high"):
        raise ToolError(f"Invalid priority: {priority}")

    with _connect() as conn:
        cur = conn.cursor()

        # Make sure the customer exists first
        cur.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if cur.fetchone() is None:
            raise ToolError(f"Customer {customer_id} does not exist.")

        cur.execute(
            """
            INSERT INTO tickets (customer_id, issue, status, priority)
            VALUES (?, ?, 'open', ?)
            """,
            (customer_id, issue, priority),
        )
        ticket_id = cur.lastrowid
        conn.commit()

        # Return the inserted row
        cur.execute(
            """
            SELECT id, customer_id, issue, status, priority, created_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        )
        row = cur.fetchone()

        if row is None:
            raise ToolError("Failed to fetch ticket after insertion.")

        return dict(row)


def get_customer_history(customer_id: int) -> Dict[str, Any]:
    """
    Return a small "view" of a customer's history:
    """
    with _connect() as conn:
        cur = conn.cursor()

        # Customer record
        cur.execute(
            """
            SELECT id, name, email, phone, status,
                   created_at, updated_at
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        )
        customer_row = cur.fetchone()
        if customer_row is None:
            raise ToolError(f"Customer {customer_id} not found.")

        # All tickets for this customer, newest first
        cur.execute(
            """
            SELECT id, customer_id, issue, status, priority, created_at
            FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (customer_id,),
        )
        tickets = [dict(r) for r in cur.fetchall()]

        return {
            "customer": dict(customer_row),
            "tickets": tickets,
        }



if __name__ == "__main__":
    print("DB path:", _db_path())
    try:
        print("\n[get_customer(1)]")
        print(get_customer(1))

        print("\n[list_customers('active', limit=5)]")
        for c in list_customers("active", 5):
            print(" -", c["id"], c["name"], c["status"])

        print("\n[update_customer(1, {'email': 'updated@example.com'})]")
        updated = update_customer(1, {"email": "updated@example.com"})
        print(updated)

        print("\n[create_ticket(1, 'Test ticket from mcp_tools', 'high')]")
        ticket = create_ticket(1, "Test ticket from mcp_tools", "high")
        print(ticket)

        print("\n[get_customer_history(1)]")
        history = get_customer_history(1)
        print("Customer:", history["customer"]["name"])
        print("Tickets:", len(history["tickets"]))

    except ToolError as e:
        print("ToolError:", e)
    except Exception as e:
        print("Unexpected error:", e)