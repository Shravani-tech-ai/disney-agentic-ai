# Disney Agentic AI — ADK + Salesforce

This project combines the existing five-agent Google ADK Disney demo with a FastAPI endpoint and a Salesforce DX package.

**Read `DEPLOYMENT_GUIDE.md` first** for the exact deployment sequence for Milestones 1–4.

- Milestone 1: three Custom Metadata Types and starter records for five agents/intents.
- Milestone 2: Apex config service, ADK callout service, controller and callout test.
- Milestone 3: FastAPI `/api/chat` wrapper invoking the existing ADK `root_agent`.
- Milestone 4: `disneyAssistant` Lightning Web Component.

All Disney data and availability are simulated. No Disney API is connected.


## Local Mock REST APIs

See `MOCK_API_IMPLEMENTATION_GUIDE.md`. Start `mock_api_server` on port 8001 before starting the ADK bridge on port 8000. All records are fictional simulation data.
