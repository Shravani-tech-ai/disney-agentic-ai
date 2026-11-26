"""Deterministic demo tools. Replace these mock datasets with authorized APIs."""

from datetime import date
from difflib import SequenceMatcher
from typing import Any


PRODUCT_KNOWLEDGE = [
    {
        "topic": "park hopper",
        "title": "Park Hopper",
        "answer": (
            "Park Hopper is a ticket option that can allow a guest to visit more "
            "than one eligible theme park on the same day, subject to the ticket's "
            "terms and current park-entry requirements."
        ),
        "source": "DEMO_KNOWLEDGE_BASE",
    },
    {
        "topic": "lightning lane multi pass",
        "title": "Lightning Lane Multi Pass",
        "answer": (
            "Lightning Lane Multi Pass is an optional paid attraction-access "
            "product. Available attractions, booking windows and rules depend "
            "on the park, date and current Disney terms."
        ),
        "source": "DEMO_KNOWLEDGE_BASE",
    },
    {
        "topic": "cancellation dining",
        "title": "Dining cancellation policy",
        "answer": (
            "Dining cancellation and no-show rules vary by restaurant and "
            "reservation. Check the specific reservation's current terms before "
            "making changes."
        ),
        "source": "DEMO_KNOWLEDGE_BASE",
    },
    {
        "topic": "ticket",
        "title": "Theme park tickets",
        "answer": (
            "Ticket options can vary by park, date, duration and add-ons. "
            "The demo does not provide current prices or inventory."
        ),
        "source": "DEMO_KNOWLEDGE_BASE",
    },
]

FAMILY_PROFILES = {
    "guest_1001": [
        {"profile_id": "P-101", "name": "Aarav Sharma", "email": "aarav@example.com"},
        {"profile_id": "P-102", "name": "Mira Sharma", "email": "mira@example.com"},
        {"profile_id": "P-103", "name": "Aarav Sharma", "email": "aarav@example.com"},
        {"profile_id": "P-104", "name": "Riya Patel", "email": "riya@example.com"},
        {"profile_id": "P-105", "name": "Riya Patil", "email": "riya.p@example.com"},
    ]
}

RESERVATIONS = {
    "RES-1001": {
        "reservation_id": "RES-1001",
        "reservation_type": "theme_park_reservation",
        "guests": [
            {"name": "Aarav Sharma", "claim_status": "CLAIMED"},
            {"name": "Mira Sharma", "claim_status": "CLAIMED"},
            {"name": "Riya Patel", "claim_status": "PENDING"},
            {"name": "Kabir Sharma", "claim_status": "NOT_LINKED"},
        ],
    }
}

DINING_SLOTS = [
    {"restaurant": "Cinderella's Royal Table", "date": "2026-11-17",
     "party_size": 4, "time": "18:45", "status": "AVAILABLE"},
    {"restaurant": "Cinderella's Royal Table", "date": "2026-11-17",
     "party_size": 4, "time": "19:20", "status": "AVAILABLE"},
    {"restaurant": "Be Our Guest", "date": "2026-11-17",
     "party_size": 4, "time": "19:00", "status": "AVAILABLE"},
    {"restaurant": "Space 220 Restaurant", "date": "2026-11-17",
     "party_size": 2, "time": "18:30", "status": "AVAILABLE"},
]

LIGHTNING_LANE_SLOTS = [
    {"park": "Magic Kingdom", "attraction": "Space Mountain",
     "date": "2026-11-17", "time": "10:30-11:30", "status": "AVAILABLE"},
    {"park": "Magic Kingdom", "attraction": "Space Mountain",
     "date": "2026-11-17", "time": "14:00-15:00", "status": "AVAILABLE"},
    {"park": "Animal Kingdom", "attraction": "Avatar Flight of Passage",
     "date": "2026-11-17", "time": "13:15-14:15", "status": "AVAILABLE"},
    {"park": "Hollywood Studios", "attraction": "Slinky Dog Dash",
     "date": "2026-11-17", "time": "16:00-17:00", "status": "AVAILABLE"},
]


def _normalise(value: str) -> str:
    return " ".join(value.lower().strip().split())


def search_product_knowledge(query: str) -> dict[str, Any]:
    """Search the local demo knowledge base for a Disney product or policy."""
    q = _normalise(query)
    matches = []
    for item in PRODUCT_KNOWLEDGE:
        score = SequenceMatcher(None, q, item["topic"]).ratio()
        if item["topic"] in q or q in item["topic"] or score >= 0.35:
            matches.append({**item, "match_score": round(score, 2)})
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return {
        "mock": True,
        "query": query,
        "results": matches[:3],
        "message": "Demo knowledge base only; verify current Disney terms."
        if matches else "No matching article found in the demo knowledge base.",
    }


def find_friends_family_duplicates(guest_id: str = "guest_1001") -> dict[str, Any]:
    """Find exact email/profile matches and possible name-similarity matches."""
    profiles = FAMILY_PROFILES.get(guest_id)
    if profiles is None:
        return {"mock": True, "error": f"No demo guest list for {guest_id}"}

    exact_groups = {}
    for p in profiles:
        email = _normalise(p.get("email", ""))
        if email:
            exact_groups.setdefault(email, []).append(p)

    duplicates = []
    for email, group in exact_groups.items():
        if len(group) > 1:
            duplicates.append({
                "type": "EXACT_EMAIL_MATCH",
                "matching_value": email,
                "profiles": group,
                "confidence": "HIGH",
            })

    possible = []
    for i, first in enumerate(profiles):
        for second in profiles[i + 1:]:
            name_score = SequenceMatcher(
                None, _normalise(first["name"]), _normalise(second["name"])
            ).ratio()
            if name_score >= 0.88 and first.get("email") != second.get("email"):
                possible.append({
                    "type": "POSSIBLE_NAME_MATCH",
                    "profiles": [first, second],
                    "name_similarity": round(name_score, 2),
                    "confidence": "REVIEW_REQUIRED",
                })

    return {
        "mock": True,
        "guest_id": guest_id,
        "profile_count": len(profiles),
        "exact_duplicates": duplicates,
        "possible_duplicates": possible,
        "note": "No profile was merged, deleted or modified.",
    }


def check_reservation_claim_status(
    reservation_id: str = "RES-1001",
) -> dict[str, Any]:
    """Return the guest claim/link status for a sample reservation."""
    reservation = RESERVATIONS.get(reservation_id)
    if not reservation:
        return {"mock": True, "error": f"Reservation {reservation_id} not found."}

    guests = reservation["guests"]
    counts = {}
    for guest in guests:
        status = guest["claim_status"]
        counts[status] = counts.get(status, 0) + 1

    return {
        "mock": True,
        "reservation_id": reservation_id,
        "reservation_type": reservation["reservation_type"],
        "guest_count": len(guests),
        "status_summary": counts,
        "guests": guests,
        "note": "Demo status only; no reservation was changed.",
    }


def search_dining_availability(
    restaurant: str,
    requested_date: str,
    party_size: int,
    preferred_time: str = "",
) -> dict[str, Any]:
    """Search mock dining slots by restaurant, date, party size and time."""
    try:
        date.fromisoformat(requested_date)
    except ValueError:
        return {"mock": True, "error": "Date must use YYYY-MM-DD."}
    if party_size < 1:
        return {"mock": True, "error": "party_size must be at least 1."}

    restaurant_q = _normalise(restaurant)
    results = [
        slot for slot in DINING_SLOTS
        if _normalise(slot["restaurant"]) == restaurant_q
        and slot["date"] == requested_date
        and slot["party_size"] >= party_size
    ]
    if preferred_time:
        results.sort(
            key=lambda s: abs(
                int(s["time"][:2]) * 60 + int(s["time"][3:5])
                - int(preferred_time[:2]) * 60 - int(preferred_time[3:5])
            )
        )
    return {
        "mock": True,
        "restaurant": restaurant,
        "date": requested_date,
        "party_size": party_size,
        "available_slots": results,
        "message": "These are simulated slots, not real Disney inventory.",
    }


def search_lightning_lane_availability(
    park: str,
    attraction: str,
    requested_date: str,
    preferred_time: str = "",
) -> dict[str, Any]:
    """Search mock Lightning Lane attraction slots."""
    try:
        date.fromisoformat(requested_date)
    except ValueError:
        return {"mock": True, "error": "Date must use YYYY-MM-DD."}

    results = [
        slot for slot in LIGHTNING_LANE_SLOTS
        if _normalise(slot["park"]) == _normalise(park)
        and _normalise(slot["attraction"]) == _normalise(attraction)
        and slot["date"] == requested_date
    ]
    return {
        "mock": True,
        "park": park,
        "attraction": attraction,
        "date": requested_date,
        "preferred_time": preferred_time or None,
        "available_slots": results,
        "message": "These are simulated slots, not real Disney inventory.",
    }
