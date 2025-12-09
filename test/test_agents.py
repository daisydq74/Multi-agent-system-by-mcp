import pytest

from agents.data_agent import CustomerDataAgent
from agents.support_agent import SupportAgentLLM
from agents.router_agent import RouterAgentLLM


@pytest.fixture
def setup_agents():
    data_agent = CustomerDataAgent()
    support_agent = SupportAgentLLM(data_agent)
    router = RouterAgentLLM(data_agent, support_agent)
    return router, data_agent, support_agent


# -----------------------------------------------------------------------------------
# Scenario 1: Task Allocation
# -----------------------------------------------------------------------------------
def test_scenario_task_allocation(setup_agents):
    router, data_agent, support_agent = setup_agents

    query = "I need help with my account, customer ID 1"
    result = router.handle_query(query)

    # Scenario should be recognized
    assert result.scenario == "task_allocation"

    # LLM output must be a string
    assert isinstance(result.final_reply, str)
    assert len(result.final_reply) > 0

    # Ensure customer data exists
    assert "customer" in result.extra
    assert isinstance(result.extra["customer"], dict)


# -----------------------------------------------------------------------------------
# Scenario 2: Negotiation / Escalation
# -----------------------------------------------------------------------------------
def test_scenario_negotiation(setup_agents):
    router, data_agent, support_agent = setup_agents

    query = "I want to cancel my subscription but I'm having billing issues, customer ID 1"
    result = router.handle_query(query)

    assert result.scenario == "negotiation_escalation"
    assert isinstance(result.final_reply, str)
    assert len(result.final_reply) > 0

    # History should be included
    assert "history" in result.extra
    assert isinstance(result.extra["history"], dict)


# -----------------------------------------------------------------------------------
# Scenario 3: Multi-step Coordination
# -----------------------------------------------------------------------------------
def test_scenario_multi_step(setup_agents):
    router, data_agent, support_agent = setup_agents

    query = "What's the status of all high-priority tickets for premium customers?"
    result = router.handle_query(query)

    assert result.scenario == "multi_step_coordination"
    assert isinstance(result.final_reply, str)
    assert len(result.final_reply) > 0

    # Ensure histories collected
    assert "premium_histories" in result.extra
    assert isinstance(result.extra["premium_histories"], list)


# -----------------------------------------------------------------------------------
# Basic DataAgent test
# -----------------------------------------------------------------------------------
def test_data_agent(setup_agents):
    _, data_agent, _ = setup_agents

    c = data_agent.fetch_customer(1)
    assert isinstance(c, dict)

    hist = data_agent.fetch_customer_history(1)
    assert isinstance(hist, dict)
