# Travelwright MAS - Fetch-A-Thon 3.0

Travelwright is a decentralized 5-Agent Multi-Agent System (MAS) built on the Fetch.ai uAgents framework. 

## Architecture
- **Orchestrator Agent (Main):** Handles ASI:One chat routing via Agent Chat Protocol (ACP).
- **Specialist Micro-agents:** Food, Transport, Route, and Payment.
- **Features:** Implements Fetch.ai Payment Protocol logic for premium features and seamless multi-agent delegation.

## How to Run
1. Install dependencies: `pip install uagents uagents-core openai python-dotenv`
2. Add your ASI API key in a `.env` file.
3. Run the master script: `python start_all.py`
4. 
