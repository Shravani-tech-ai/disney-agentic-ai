# Disney Agentic AI — Salesforce Milestones 1–4

This package contains: **M1** Custom Metadata Types and starter records; **M2** Apex configuration + callout/controller; **M3** FastAPI wrapper for your existing Google ADK orchestrator; **M4** Lightning Web Component chat UI. All Disney-side records and availability remain mock data.

## 0. Prerequisites
- Salesforce CLI (`sf`) installed and authenticated to your Personal Developer Edition.
- Python 3.11 recommended. Existing `disney_assistant/agent.py` and `tools.py` are retained from your starter project.
- A Gemini API key configured as `GOOGLE_API_KEY` for the Python process. Never put it in Salesforce.
- Update ngrok before exposing your local API: your earlier agent version was 3.23.3; the account required at least 3.29.0. Or use another secure HTTPS tunnel.

## 1. Start the Python ADK API (Milestone 3)
From the extracted `disney_agentic_ai` folder:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Check `http://127.0.0.1:8000/health`. POST test at `http://127.0.0.1:8000/api/chat` with:

```json
{ "session_id":"SF-DEMO-1", "user_id":"salesforce-demo-user", "message":"What is Park Hopper?", "configuration":{"mock_mode":true,"enabled_agents":["ProductKnowledgeAgent","FriendsFamilyDuplicateAgent","ReservationPartialClaimAgent","DiningAvailabilityAgent","LightningLaneAvailabilityAgent"]}}
```

The API uses the existing `root_agent` and an in-memory ADK session service. Sessions reset when the Python process restarts. The `intent` and `selected_agents` fields are display hints for this MVP; actual specialist routing remains in the ADK orchestrator. The agent's natural-language answer is authoritative.

## 2. Expose API over HTTPS
Salesforce cannot call `localhost` on your PC. For local development, expose port 8000 through a secure HTTPS tunnel (for example ngrok) and copy its HTTPS forwarding URL. Keep the tunnel running. Do not publish the Gemini key.

## 3. Deploy Salesforce source (Milestones 1 and 2)
Open PowerShell in `disney_agentic_ai\salesforce`:

```powershell
sf org login web --alias DisneyDev --instance-url https://login.salesforce.com
sf project deploy start --target-org DisneyDev --source-dir force-app
```

If you already authenticated your org, skip login and use your existing alias. Deploying creates the three Custom Metadata Types, their fields/records, three Apex classes, Apex tests, and the LWC bundle.

## 4. Create the Named Credential
In Salesforce Setup:
1. Search **Named Credentials**.
2. Open **Named Credentials** and click **New** (or create a new External Credential + Named Credential if your org shows the newer UI).
3. Label: `Disney ADK`; Name: `Disney_ADK_NC`.
4. URL: paste the HTTPS tunnel base URL only, e.g. `https://xxxx.ngrok-free.app` (no `/api/chat`).
5. For a local demo, choose **No Authentication** only if the tunnel URL is private/unshared. Prefer adding an API-key header / authenticated gateway before any shared or production use.
6. Save. The Apex endpoint is `callout:Disney_ADK_NC/api/chat`.

If your org uses the newer External Credential flow, create a suitable External Credential and principal, grant principal access to the user/profile running the LWC, then associate it with this Named Credential. This package intentionally does not hardcode credentials.

## 5. Add the component to an app page (Milestone 4)
1. Setup → **Lightning App Builder** → New → App Page.
2. Name it `Disney Assistant`. Choose a one-column layout.
3. Drag **Disney Assistant** from Custom components onto the page.
4. Save → Activate → assign it to your app/profile as desired.
5. Open the page and send a test prompt.

## 6. Suggested tests
- `What is Park Hopper?`
- `Check my Friends and Family list for duplicate people.`
- `Who has not claimed reservation RES-1001?`
- `Find a table for four at Cinderella's Royal Table on 2026-11-17 around 19:00.`
- `Is Space Mountain available for Lightning Lane at Magic Kingdom on 2026-11-17?`

## 7. Configuration through Custom Metadata
Setup → Custom Metadata Types → **Disney Agent Config** to activate/deactivate agent registry records; **Disney Intent Routing** controls whether an intent is enabled; **Disney Integration Config** controls mock mode and service active state. Changes take effect without redeploying Apex. Do not store API keys/passwords in Custom Metadata.

## Important notes / known MVP limitations
- No Disney API is connected. All data remains simulated.
- The ADK endpoint runs in-process and stores sessions in memory. Use a persistent session store and authenticated, rate-limited HTTPS service before production.
- The MVP response parser returns the final ADK text. Structured `data` is currently `{}`; richer typed outputs can be added after the first end-to-end test.
- The backend's `intent`/`selected_agents` fields are a simple UI hint. Do not use them for authorization or business decisions. ADK remains responsible for actual agent routing.
- Apex test uses `HttpCalloutMock`; run Apex tests after deploy.
- Salesforce API version is 66.0; if your org does not support it yet, change `apiVersion` in the Apex and LWC metadata and `sourceApiVersion` in `sfdx-project.json` to the highest API version available in your org.
