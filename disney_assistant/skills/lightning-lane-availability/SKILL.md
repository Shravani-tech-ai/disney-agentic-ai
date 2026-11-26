---
name: lightning-lane-availability
description: Use when a user asks for Lightning Lane or attraction time-slot availability at a specific Disney park and on a specific date.
---

# Lightning Lane Availability Skill

## Objective
Find simulated Lightning Lane attraction slots.

## Available tool
- `search_lightning_lane_availability(park, attraction, requested_date, preferred_time)`

## Required information
- Park
- Attraction
- Date in YYYY-MM-DD format

Preferred time is optional.

## Workflow

1. Extract the park, attraction and date.
2. Ask a focused question if any required value is missing.
3. Extract the preferred time if supplied.
4. Call `search_lightning_lane_availability`.
5. Inspect the returned slots.
6. Present matching times and availability status.
7. If no slots are returned, explain that the mock dataset has no matching slots.

## Rules

- Never invent attraction availability.
- Never substitute another park or attraction.
- Do not confuse Lightning Lane product explanations with attraction availability.
- Never purchase, select or hold a slot.
- Clearly state that results are simulated demo data.
