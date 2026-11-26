---
name: dining-availability
description: Use when a user wants to find restaurant tables, dining reservation slots, meal availability, or available dining times.
---

# Dining Availability Skill

## Objective
Find simulated restaurant availability using the Dining REST API.

## Available tool
- `search_dining_availability(restaurant, requested_date, party_size, preferred_time)`

## Required information
- Restaurant
- Date in YYYY-MM-DD format
- Party size

Preferred time is optional.

## Workflow

1. Extract the restaurant, date and party size.
2. Ask a focused question if any required value is missing.
3. Extract the preferred time if supplied.
4. Call `search_dining_availability`.
5. Inspect the returned available slots.
6. Present the available times clearly.
7. If no slots are returned, explain that the mock dataset
   has no matching availability.

## Rules

- Never invent restaurant availability.
- Never change the requested party size or date.
- Do not treat an empty result as a confirmed real-world
  restaurant closure.
- Never book or hold a table.
- Clearly state that results are simulated, not real Disney inventory.
