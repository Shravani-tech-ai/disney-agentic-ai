---
name: friends-family-duplicates
description: Use when a user asks to find duplicate people, repeated profiles, matching guests, or possible duplicate Friends and Family records.
---

# Friends & Family Duplicate Detection Skill

## Objective
Identify exact and possible duplicate guest profiles.

## Available tool
- `find_friends_family_duplicates(guest_id)`

## Workflow

1. Identify the guest ID from the user's request.
2. If the guest ID is missing, ask the user for it.
3. Call `find_friends_family_duplicates` with the guest ID.
4. Inspect exact matches and possible matches separately.
5. Explain why each record was flagged.
6. Clearly distinguish confirmed matching email addresses
   from possible name similarities.

## Rules

- An exact email match is stronger evidence than a name match.
- Similar names do not prove two records belong to the same person.
- Do not recommend automatic merging based only on similarity.
- Never merge, delete or modify profiles.
- Report that the results are simulated demo data.
