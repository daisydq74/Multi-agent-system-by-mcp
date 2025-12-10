# Multi-Agent Customer Support MCP
A lightweight multi-agent customer support demo that exposes database tools via an MCP server and orchestrates local LLM calls for responses.

## What this project does
- Exposes customer and ticket management tools through a FastMCP server backed by SQLite.
- Routes user queries to specialized agents (router, data, support) for retrieval, escalation, and reporting workflows.
- Connects to a local LLM endpoint to generate natural-language support replies.
- Includes a seeded demo database plus scripts and tests to exercise the toolchain.

## Architecture Overview
This system pairs a FastMCP server (tool layer) with three Python agents. The RouterAgentLLM decides which scenario to run, the CustomerDataAgent fetches data directly from the MCP tool helpers, and the SupportAgentLLM crafts replies via a local LLM HTTP API. All tools operate on the SQLite `support.db` database.

```
+---------+        +-----------------+        +------------------+
|  User   | -----> |  RouterAgentLLM | -----> | SupportAgentLLM  |
|  query  |        |  (classification)|        | (calls LLM HTTP) |
+---------+        +-----------------+        +------------------+
        |                       |                        |
        |                       v                        |
        |              CustomerDataAgent                 |
        |                       |                        |
        |                       v                        |
        |             MCP tools (mcp_server/mcp_tools.py)|
        |                       |                        |
        |                       v                        v
        |                  SQLite support.db      Local LLM API
        |                                  (http://localhost:11434)
        +----------------------------------------------------------
```

## Repo Structure
```
.
├── README.md
├── Multi-Agent Customer Support System using Local LLM.ipynb
├── agents/                # Router, data, and support agents
├── anaconda_projects/
├── database_setup.py      # Creates/seeds the SQLite database
├── mcp_server/            # FastMCP server and shared tool functions
├── support.db             # SQLite database (created/seeded locally)
└── test/                  # Pytest-based checks for tools and agents
```

## Setup
- **Python version:** Python 3.10+ recommended.
- **Install dependencies:**
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install mcp requests
  ```

If `support.db` is missing or you want fresh data, initialize it:
```bash
python database_setup.py
```
(The script offers to insert sample customers and tickets.)

## Configuration
- **Database path:** Tools read `support.db` by default from the repository root (resolved relative to `mcp_server/mcp_tools.py`). No environment variables are required.
- **LLM endpoint:** `SupportAgentLLM` and `RouterAgentLLM` send requests to `http://localhost:11434/api/generate`; ensure a compatible local model (e.g., DeepSeek) is running there.

## How to Run
- **Start the MCP server:**
  ```bash
  python mcp_server/mcp_server.py
  ```
  The server registers tools such as `get_customer`, `list_customers`, `update_customer`, `create_ticket`, and `get_customer_history`.

- **Run the database/tool smoke test:**
  ```bash
  python mcp_server/mcp_tools.py
  ```
  This exercises the tool helpers directly and confirms the database is reachable.

- **Exercise agent flows (via tests):**
  ```bash
  pytest test/test_agents.py
  pytest test/test_mcp_tools.py
  ```
  These drive the router, data, and support agents and validate tool behavior.

## Demo / Example Queries
Try these prompts through the router or directly through the MCP tools:
1. "Show the profile for customer ID 1."
2. "List up to 5 active customers."
3. "Update customer 3 to disabled status." (via `update_customer`)
4. "Create a high-priority ticket for customer 2: billing payment keeps failing."
5. "Give me the full ticket history for customer 5."

Logs and tool outputs are printed to stdout; no additional log files are created by default.
