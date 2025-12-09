import pytest

from agents.data_agent import CustomerDataAgent
from agents.support_agent import SupportAgent
from agents.router_agent import RouterAgent


@pytest.fixture
def setup_agents():
    """Initialize all agents for testing."""
    data_agent = CustomerDataAgent()
    support_agent = SupportAgent(data_agent)
    router = RouterAgent(data_agent, support_agent)
    return router, data_agent, support_agent


# -------------------------------------------------------------------------
# Scenario 1: Task Allocation
# -------------------------------------------------------------------------
def test_scenario_task_allocation(setup_agents):
    router, data_agent, support_agent = setup_agents

    query = "I need help with my account, customer ID 1"
    result = router.handle_query(query)

    # Scenario detection
    assert result.scenario == "task_allocation"

    # Final reply should include customer name or ID
    assert "Customer found" in result.final_reply or "customer" in result.final_reply.lower()

    # Router logs should show A2A actions
    assert any("fetching customer" in log.lower() for log in result.logs)
    assert any("support-agent" in log.lower() for log in result.logs)


# -------------------------------------------------------------------------
# Scenario 2: Negotiation / Escalation
# -------------------------------------------------------------------------
def test_scenario_negotiation(setup_agents):
    router, data_agent, support_agent = setup_agents

    query = "I want to cancel my subscription but I'm having billing issues, customer ID 1"
    result = router.handle_query(query)

    # Scenario detection
    assert result.scenario == "negotiation_escalation"

    # Final reply should include escalation/billing language
    assert "billing" in result.final_reply.lower()
    assert "cancellation" in result.final_reply.lower()

    # Should create a new ticket (verification via DataAgent)
    assert "high-priority" in result.final_reply.lower() or "high priority" in result.final_reply.lower()

    # Logs should reflect multi-step coordination
    assert any("customer history" in log.lower() for log in result.logs)
    assert any("refund" in result.final_reply.lower() for log in result.logs)


# -------------------------------------------------------------------------
# Scenario 3: Multi-step Coordination
# -------------------------------------------------------------------------
def test_scenario_multi_step(setup_agents):
    router, data_agent, support_agent = setup_agents

    query = "What's the status of all high-priority tickets for premium customers?"
    result = router.handle_query(query)

    assert result.scenario == "multi_step_coordination"

    # Must produce a report
    assert "premium customers" in result.final_reply.lower()
    assert "high-priority" in result.final_reply.lower() or "high priority" in result.final_reply.lower()

    # Logs should show multi-step delegation
    assert any("premium customers" in log.lower() for log in result.logs)
    assert any("report" in log.lower() for log in result.logs)


# -------------------------------------------------------------------------
# Fallback Scenario (no matching intent)
# -------------------------------------------------------------------------
def test_scenario_fallback(setup_agents):
    router, _, _ = setup_agents

    query = "Tell me a joke about databases"
    result = router.handle_query(query)

    assert result.scenario == "fallback"
    assert "could not classify" in result.final_reply.lower()


# -------------------------------------------------------------------------
# Additional: direct DataAgent functionality
# -------------------------------------------------------------------------
def test_data_agent_fetch_customer(setup_agents):
    _, data_agent, _ = setup_agents

    result = data_agent.fetch_customer(1)
    assert isinstance(result, dict)
    assert "id" in result or "error" in result
