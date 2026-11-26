# Disney Agentic AI – Local Mock REST API implementation

All provider data in this project is fictional and for development/testing only. It is not a Disney API, is not affiliated with Disney, and does not make real reservations or purchases.

## Architecture

- Salesforce LWC -> Apex -> FastAPI ADK bridge (`127.0.0.1:8000/api/chat`)
- ADK specialist tools -> HTTP (`httpx`) -> mock provider API (`127.0.0.1:8001/mock-api/...`)
- Mock provider API -> JSON datasets in `mock_api_server/data/`

## 1. Setup

Use the same virtual environment at the project root. Activate it and install dependencies:

```powershell
cd C:\Users\202454\Desktop\disney_agentic_ai
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Put your Gemini API key in `.env`. The ADK bridge loads the environment through your existing startup setup if configured; if it does not, set it in the PowerShell session with `$env:GOOGLE_API_KEY = \"YOUR_KEY\"`. Keep the key private.

## 2. Start the mock provider API (Terminal 1)

```powershell
cd C:\Users\202454\Desktop\disney_agentic_ai
.\.venv\Scripts\Activate.ps1
python -m uvicorn mock_api_server.main:app --host 127.0.0.1 --port 8001 --reload
```

Open `http://127.0.0.1:8001/docs`. Check `http://127.0.0.1:8001/health`.

## 3. Start the ADK + Salesforce bridge (Terminal 2)

```powershell
cd C:\Users\202454\Desktop\disney_agentic_ai
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

The bridge's existing `/api/chat` endpoint remains the Salesforce entry point. Its ADK tools now call the mock REST APIs over HTTP. The `mock_mode` flag in the Salesforce request should remain `true` because all provider records are simulated.

## 4. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/mock-api/products?keyword=MagicBand` | Product catalogue |
| GET | `/mock-api/knowledge/search?query=park%20hopper` | Product/policy knowledge |
| POST | `/mock-api/friends-family/check-duplicates` | Duplicate profile detection |
| GET | `/mock-api/reservations/RES-1001/claim-status` | Reservation guest claim status |
| POST | `/mock-api/dining/availability` | Restaurant time slots |
| POST | `/mock-api/lightning-lane/availability` | Attraction return windows |

## 5. Example PowerShell tests

```powershell
Invoke-RestMethod 'http://127.0.0.1:8001/mock-api/products?keyword=MagicBand'
Invoke-RestMethod 'http://127.0.0.1:8001/mock-api/knowledge/search?query=park%20hopper'
Invoke-RestMethod 'http://127.0.0.1:8001/mock-api/reservations/RES-1001/claim-status'

$body = @{ guest_id = 'GUEST-1001' } | ConvertTo-Json
Invoke-RestMethod 'http://127.0.0.1:8001/mock-api/friends-family/check-duplicates' -Method Post -ContentType 'application/json' -Body $body

$body = @{ restaurant = "Cinderella's Royal Table"; date = '2026-12-15'; party_size = 4; preferred_time = '19:00' } | ConvertTo-Json
Invoke-RestMethod 'http://127.0.0.1:8001/mock-api/dining/availability' -Method Post -ContentType 'application/json' -Body $body

$body = @{ park = 'Magic Kingdom'; attraction = 'Space Mountain'; date = '2026-12-15' } | ConvertTo-Json
Invoke-RestMethod 'http://127.0.0.1:8001/mock-api/lightning-lane/availability' -Method Post -ContentType 'application/json' -Body $body
```

## 6. Test full ADK routing

With both servers running, send the normal Salesforce-style request to `http://127.0.0.1:8000/api/chat`. The orchestrator chooses the specialist; the specialist calls the corresponding API tool. Use a unique `session_id` per test conversation.

## 7. Change mock data

Edit JSON files in `mock_api_server/data/`. The API reads the files on each request, so restart is not normally required. Keep IDs consistent across `guests.json` and `reservations.json` where appropriate.

## 8. Salesforce note

No Salesforce metadata needs to be redeployed for this backend-only change. Salesforce continues calling `callout:Disney_ADK_NC/api/chat`. For local testing from Salesforce, the Salesforce cloud cannot call your computer's `127.0.0.1`; use an HTTPS tunnel such as ngrok to expose port 8000, and keep port 8001 private because only the local ADK backend needs it.
