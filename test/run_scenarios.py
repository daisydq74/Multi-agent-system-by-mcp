# run_scenarios.py
# -----------------------
# Auto-run 8 scenarios and save the output into results.txt


from agents.router_agent import RouterAgentLLM
from agents.data_agent import CustomerDataAgent
from agents.support_agent import SupportAgentLLM


# -----------------------
# Create agent instances
# -----------------------
data_agent = CustomerDataAgent()
support_agent = SupportAgentLLM(data_agent)
router = RouterAgentLLM(data_agent, support_agent)


# -----------------------
# Define the 8 scenario queries
# -----------------------
SCENARIOS = [
    "Get customer information for ID 5",
    "I'm customer 12345 and need help upgrading my account",
    "Show me all active customers who have open tickets",
    "I've been charged twice, please refund immediately!",
    "Update my email to new@email.com and show my ticket history",
    "I need help with my account, customer ID 1",
    "I want to cancel my subscription but I'm having billing issues, customer ID 1",
    "What's the status of all high-priority tickets for premium customers?"
]


# -----------------------
# Helper: format output
# -----------------------
def format_result(query, result):
    txt = []
    txt.append("=" * 80)
    txt.append(f"USER QUERY: {query}")
    txt.append("=" * 80)

    txt.append(f"\n[Detected scenario]: {result.scenario}\n")

    if result.logs:
        txt.append("--- LOGS ---")
        for line in result.logs:
            txt.append(line)

    txt.append("\n--- FINAL RESPONSE ---")
    txt.append(result.final_reply)

    if result.extra:
        txt.append("\n--- EXTRA DATA ---")
        txt.append(str(result.extra))

    txt.append("\n")
    return "\n".join(txt)


# -----------------------
# Main execution
# -----------------------
def main():
    output = []

    for q in SCENARIOS:
        result = router.handle_query(q)
        formatted = format_result(q, result)
        output.append(formatted)
        print(formatted)   # also show in console

    # Save to file
    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(output))

    print("\nSaved all scenario outputs to results.txt")


if __name__ == "__main__":
    main()
