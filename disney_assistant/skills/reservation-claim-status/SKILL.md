---
name: reservation-claim-status
description: Use when a user asks who has claimed, linked, accepted, or not linked an existing reservation, or why only some guests can see it.
---

# Reservation Claim Status Skill

## Objective
Inspect guest claim and linking status for an existing reservation.

## Available tool
- `check_reservation_claim_status(reservation_id)`

## Workflow

1. Extract the reservation ID.
2. If it is missing, ask the user for it.
3. For this demo, use RES-1001 only if the user clearly
   refers to the sample reservation.
4. Call `check_reservation_claim_status`.
5. Read the guest list and status summary.
6. Group guests by their returned claim status.
7. Explain which guests have claimed, are pending,
   or are not linked.

## Rules

- Do not assume a guest has claimed a reservation.
- Use only the returned status information.
- Never claim that a reservation was modified.
- Never confuse an existing reservation's guest-linking
  status with dining availability.
- Identify results as simulated demo data.
