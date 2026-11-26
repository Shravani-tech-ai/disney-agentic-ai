
"""ADK tools that communicate with the local Disney mock REST APIs."""

from typing import Any

from .provider_api_client import get, post


def search_products(keyword: str) -> dict[str, Any]:
    """Search Disney products by keyword using the Products REST API."""
    return get("/mock-api/products", params={"keyword": keyword})


def search_product_knowledge(query: str) -> dict[str, Any]:
    """Search Disney policies, guides and informational articles."""
    return get("/mock-api/knowledge/search", params={"query": query})


def find_friends_family_duplicates(
    guest_id: str = "GUEST-1001",
) -> dict[str, Any]:
    """Find possible duplicate profiles in a guest's Friends & Family list."""
    return post(
        "/mock-api/friends-family/check-duplicates",
        {"guest_id": guest_id},
    )


def check_reservation_claim_status(
    reservation_id: str = "RES-1001",
) -> dict[str, Any]:
    """Check the claim and linking status of reservation guests."""
    return get(
        f"/mock-api/reservations/{reservation_id}/claim-status"
    )


def search_dining_availability(
    restaurant: str,
    requested_date: str,
    party_size: int,
    preferred_time: str = "",
) -> dict[str, Any]:
    """Search simulated restaurant availability."""
    return post(
        "/mock-api/dining/availability",
        {
            "restaurant": restaurant,
            "date": requested_date,
            "party_size": party_size,
            "preferred_time": preferred_time,
        },
    )


def search_lightning_lane_availability(
    park: str,
    attraction: str,
    requested_date: str,
    preferred_time: str = "",
) -> dict[str, Any]:
    """Search simulated Lightning Lane availability."""
    return post(
        "/mock-api/lightning-lane/availability",
        {
            "park": park,
            "attraction": attraction,
            "date": requested_date,
            "preferred_time": preferred_time,
        },
    )
