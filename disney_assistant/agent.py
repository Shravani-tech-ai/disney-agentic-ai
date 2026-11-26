
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

Use your product-knowledge skill to decide how to handle
product information and general knowledge requests.

Use the available REST API tools to retrieve information.
Never invent product details, prices or policies.

If the requested information is unavailable, explain that
the demo dataset does not contain it.

All information comes from simulated data.
""",

    tools=[
        search_products,
        search_product_knowledge,
        product_skill_toolset,
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

Use your friends-family-duplicates skill to guide the
duplicate detection workflow.

Use the available REST API tool to inspect guest profiles.
Explain why records were flagged.

Never merge, delete or modify profiles.
All results are simulated demo data.
""",

    tools=[
        find_friends_family_duplicates,
        friends_family_skill_toolset,
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

Use your reservation-claim-status skill to guide the
reservation claim workflow.

Use the available REST API tool to retrieve guest statuses.
Ask for a reservation ID if it is missing.

Never claim to have modified a real reservation.
All results are simulated demo data.
""",

    tools=[
        check_reservation_claim_status,
        reservation_skill_toolset,
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
You are the Dining Availability specialist.

Use your dining-availability skill to guide the dining
search workflow.

Use the available REST API tool to retrieve matching slots.

Ask for missing required information rather than inventing it.
Never book or hold a table.

All results are simulated demo data, not real Disney inventory.
""",

    tools=[
        search_dining_availability,
        dining_skill_toolset,
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
You are the Lightning Lane Availability specialist.

Use your lightning-lane-availability skill to guide the
attraction availability workflow.

Use the available REST API tool to retrieve matching slots.

Ask for missing required information.
Never purchase, select or hold a slot.

All results are simulated demo data, not real Disney inventory.
""",

    tools=[
        search_lightning_lane_availability,
        lightning_lane_skill_toolset,
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
