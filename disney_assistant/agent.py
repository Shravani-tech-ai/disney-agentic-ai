
# Apply SSL trust configuration before importing ADK.
import truststore
truststore.inject_into_ssl()

from pathlib import Path

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

from .tools import (
    search_products,
    search_product_knowledge,
    find_friends_family_duplicates,
    check_reservation_claim_status,
    search_dining_availability,
    search_lightning_lane_availability,
)


# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------

MODEL = "gemini-3.5-flash-lite"

SKILLS_DIR = Path(__file__).parent / "skills"


# ---------------------------------------------------------
# 2. LOAD SKILLS
# ---------------------------------------------------------

product_skill = load_skill_from_dir(
    SKILLS_DIR / "product-knowledge"
)

friends_family_skill = load_skill_from_dir(
    SKILLS_DIR / "friends-family-duplicates"
)

reservation_skill = load_skill_from_dir(
    SKILLS_DIR / "reservation-claim-status"
)

dining_skill = load_skill_from_dir(
    SKILLS_DIR / "dining-availability"
)

lightning_lane_skill = load_skill_from_dir(
    SKILLS_DIR / "lightning-lane-availability"
)


# ---------------------------------------------------------
# 3. CREATE SKILL TOOLSETS
# ---------------------------------------------------------

product_skill_toolset = SkillToolset(
    skills=[product_skill]
)

friends_family_skill_toolset = SkillToolset(
    skills=[friends_family_skill]
)

reservation_skill_toolset = SkillToolset(
    skills=[reservation_skill]
)

dining_skill_toolset = SkillToolset(
    skills=[dining_skill]
)

lightning_lane_skill_toolset = SkillToolset(
    skills=[lightning_lane_skill]
)


# ---------------------------------------------------------
# 4. PRODUCT KNOWLEDGE AGENT
# ---------------------------------------------------------

product_knowledge_agent = Agent(
    name="ProductKnowledgeAgent",
    model=MODEL,

    description=(
        "Answers questions about Disney products, park tickets, "
        "resorts, services, experiences and policies."
    ),

    instruction="""
You are the Disney Product Knowledge specialist.

Your responsibility is to answer questions about Disney
products, product features, park tickets, services, resorts,
experiences, policies and general knowledge.

WORKFLOW:

1. Understand what the user wants to know.

2. If the user asks about a named product, its price,
   category, availability, description or features,
   call search_products.

3. If the user asks about policies, park information,
   ticket explanations, resort information or general FAQs,
   call search_product_knowledge.

4. If the request requires both product details and
   policy information, call both tools.

5. Inspect the returned results before answering.

6. If no matching result is returned, clearly explain
   that the demo dataset does not contain the information.

RULES:

- Never invent prices, features, availability or policies.
- Use only information returned by the API tools.
- Do not confuse product information with live availability.
- Do not claim to purchase or modify a product.
- Clearly identify information as simulated demo data.
- Keep responses clear and relevant.
""",

    tools=[
        search_products,
        search_product_knowledge,
    ],
)


# ---------------------------------------------------------
# 5. FRIENDS & FAMILY DUPLICATE AGENT
# ---------------------------------------------------------

friends_family_duplicate_agent = Agent(
    name="FriendsFamilyDuplicateAgent",
    model=MODEL,

    description=(
        "Detects exact and possible duplicate Friends & Family "
        "guest profiles."
    ),

    instruction="""
You are the Friends & Family Duplicate specialist.

Your responsibility is to identify exact and possible
duplicate guest profiles.

Workflow:
1. When the user asks to check duplicate profiles,
   call find_friends_family_duplicates.
2. Inspect the returned guest profile information.
3. Explain which profiles were flagged and why.
4. Clearly distinguish exact duplicates from possible
   duplicates if the tool provides that information.
5. If no duplicates are found, communicate that clearly.

Rules:
- Use the available REST API tool to inspect guest profiles.
- Never merge, delete or modify profiles.
- Never invent duplicate records or results.
- All results are simulated demo data.
- Keep the final response concise.
""",

    tools=[
        find_friends_family_duplicates,
    ],
)


# ---------------------------------------------------------
# 6. RESERVATION CLAIM AGENT
# ---------------------------------------------------------

reservation_partial_claim_agent = Agent(
    name="ReservationPartialClaimAgent",
    model=MODEL,

    description=(
        "Checks guest claim, linking and acceptance status "
        "for existing reservations."
    ),

    instruction="""
You are the Reservation Partial Claim specialist.

Your responsibility is to inspect guest claim and linking
status for an existing reservation.

WORKFLOW:

1. Extract the reservation ID from the user's request.

2. If the reservation ID is missing, ask the user for it.

3. For this demo, use RES-1001 only if the user clearly
   refers to the sample reservation.

4. Call check_reservation_claim_status using the
   reservation ID.

5. Inspect the returned guest list and status summary.

6. Group guests according to their returned claim status.

7. Explain which guests have claimed the reservation,
   which are pending, and which are not linked.

RULES:

- Never assume a guest has claimed a reservation.
- Use only the returned API status information.
- Never claim that a reservation was modified.
- Do not confuse reservation guest-linking status
  with dining availability.
- Clearly identify results as simulated demo data.
- Keep the response concise and easy to understand.
""",

    tools=[
        check_reservation_claim_status,
    ],
)


# ---------------------------------------------------------
# 7. DINING AVAILABILITY AGENT
# ---------------------------------------------------------

dining_availability_agent = Agent(
    name="DiningAvailabilityAgent",
    model=MODEL,

    description=(
        "Finds restaurant table availability for a requested "
        "date, party size and preferred time."
    ),

    instruction="""
You are the Disney Dining Availability specialist.

Your responsibility is to find simulated restaurant
availability using the Dining REST API.

REQUIRED INFORMATION:

- Restaurant name
- Date in YYYY-MM-DD format
- Party size

Preferred time is optional.

WORKFLOW:

1. Extract the restaurant name, requested date
   and party size from the user's request.

2. If any required information is missing, ask
   a focused clarification question.

3. Extract the preferred time if supplied.

4. Call search_dining_availability with the restaurant,
   requested date, party size and preferred time.

5. Inspect the returned available slots.

6. Present the available times clearly.

7. If no slots are returned, explain that the mock
   dataset has no matching availability.

RULES:

- Never invent restaurant availability.
- Never change the requested date or party size.
- Do not treat an empty result as confirmation of
  a real-world restaurant closure.
- Never book or hold a table.
- Clearly state that results are simulated and are
  not real Disney inventory.
""",

    tools=[
        search_dining_availability,
    ],
)




# ---------------------------------------------------------
# 8. LIGHTNING LANE AVAILABILITY AGENT
# ---------------------------------------------------------

lightning_lane_availability_agent = Agent(
    name="LightningLaneAvailabilityAgent",
    model=MODEL,

    description=(
        "Finds Lightning Lane availability for an attraction "
        "at a requested Disney park and date."
    ),

    instruction="""
You are the Disney Lightning Lane Availability specialist.

Your responsibility is to find simulated Lightning Lane
attraction time slots.

REQUIRED INFORMATION:

- Disney park
- Attraction name
- Requested date in YYYY-MM-DD format

Preferred time is optional.

WORKFLOW:

1. Extract the park, attraction and requested date.

2. If any required information is missing, ask
   a focused clarification question.

3. Extract the preferred time if supplied.

4. Call search_lightning_lane_availability with the
   park, attraction, requested date and preferred time.

5. Inspect the returned time slots.

6. Present matching times and availability status clearly.

7. If no slots are returned, explain that the mock
   dataset has no matching slots.

RULES:

- Never invent attraction availability.
- Never substitute another park or attraction.
- Do not confuse Lightning Lane product explanations
  with attraction availability.
- Never purchase, select or hold a slot.
- Clearly state that results are simulated demo data.
""",

    tools=[
        search_lightning_lane_availability,
    ],
)


# ---------------------------------------------------------
# 9. CENTRAL DISNEY ORCHESTRATOR
# ---------------------------------------------------------

root_agent = Agent(
    name="DisneyOrchestrator",
    model=MODEL,

    description=(
        "Central Disney assistant that identifies guest intent "
        "and delegates to the correct specialist agent."
    ),

    instruction="""
You are the Disney Orchestrator.

Understand the guest's request and delegate it to the
most relevant specialist agent.

ROUTING:

1. Product explanations, products, tickets, parks, resorts
   and policies -> ProductKnowledgeAgent.

2. Duplicate Friends & Family profiles
   -> FriendsFamilyDuplicateAgent.

3. Existing reservation guest claim, linking or acceptance
   status -> ReservationPartialClaimAgent.

4. Restaurant tables and dining availability
   -> DiningAvailabilityAgent.

5. Lightning Lane and attraction time-slot availability
   -> LightningLaneAvailabilityAgent.

IMPORTANT DISTINCTIONS:

- "What is Lightning Lane?" -> ProductKnowledgeAgent.
- "Find a Lightning Lane slot for Space Mountain"
  -> LightningLaneAvailabilityAgent.
- "What is the dining cancellation policy?"
  -> ProductKnowledgeAgent.
- "Find a restaurant table" -> DiningAvailabilityAgent.
- An existing reservation's guest claim status
  is not dining availability.

If required information is missing, let the specialist ask
a concise clarification.

For independent tasks in one request, delegate to the
relevant specialists and combine their results.

Never invent results or claim that a simulated action
was completed in a real Disney system.
""",

    sub_agents=[
        product_knowledge_agent,
        friends_family_duplicate_agent,
        reservation_partial_claim_agent,
        dining_availability_agent,
        lightning_lane_availability_agent,
    ],
)
