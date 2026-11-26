from disney_assistant.tools import (
    find_friends_family_duplicates,
    check_reservation_claim_status,
    search_dining_availability,
    search_lightning_lane_availability,
    search_product_knowledge,
)


def test_product_knowledge():
    result = search_product_knowledge("What is Park Hopper?")
    assert result["mock"] is True
    assert result["results"]


def test_duplicate_detection():
    result = find_friends_family_duplicates("guest_1001")
    assert result["profile_count"] == 5
    assert result["exact_duplicates"]


def test_reservation_partial_claim():
    result = check_reservation_claim_status("RES-1001")
    assert result["status_summary"]["CLAIMED"] == 2
    assert result["status_summary"]["PENDING"] == 1


def test_dining_availability():
    result = search_dining_availability(
        "Cinderella's Royal Table", "2026-11-17", 4, "19:00"
    )
    assert len(result["available_slots"]) == 2


def test_lightning_lane_availability():
    result = search_lightning_lane_availability(
        "Magic Kingdom", "Space Mountain", "2026-11-17"
    )
    assert len(result["available_slots"]) == 2
