import requests
import json


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



class SupportAgentLLM:
    def __init__(self, data_agent):
        self.data_agent = data_agent
        self.model = "deepseek-r1:8b"

    # Scenario 1: Account help
    def account_help(self, customer, query):
        prompt = f"""
You are a helpful customer support assistant.

Customer data:
{customer}

User query:
{query}

Write a friendly, concise, and professional answer.
"""
        reply = LLM(prompt, self.model)
        return reply

    # Scenario 2: Billing + cancellation escalation
    def billing_escalation(self, history, query):
        prompt = f"""
You are a senior support agent handling a cancellation + billing conflict.

Customer full history:
{history}

User request:
"{query}"

Provide:
1. A short confirmation of the issue
2. Billing investigation steps
3. Ticket creation recommendation
4. Refund considerations
5. Next actions

Write in helpful natural language.
"""
        reply = LLM(prompt, self.model)
        return reply

    # Scenario 3: High priority ticket report
    def high_priority_report(self, histories):
        prompt = f"""
You are analyzing multiple premium customers' high-priority tickets.

All customer histories:
{histories}

Write a structured report with:
- Customer name + ID
- Count of high-priority tickets
- Any unresolved or critical issues
- One-sentence recommendation per customer
"""
        reply = LLM(prompt, self.model)
        return reply
