---
name: product-knowledge
description: Use when answering questions about Disney products, product features, product information, park tickets, services, resorts, experiences, policies, and general knowledge.
---

# Product Knowledge Skill

## Objective
Retrieve accurate product and informational content from the Disney mock REST APIs.

## Available tools
- `search_products(keyword)` searches the Products API.
- `search_product_knowledge(query)` searches the Knowledge API.

## Workflow

1. Understand what the user wants to know.
2. If the user asks about a named product, its price, category,
   availability, description or features, call `search_products`.
3. If the user asks about policies, park information, ticket
   explanations, resort information or general FAQs, call
   `search_product_knowledge`.
4. If the request needs both product details and policy information,
   call both tools.
5. Inspect the returned results before answering.
6. If no matching result is returned, clearly say that the demo
   data does not contain the requested information.

## Rules

- Never invent prices, features, availability or policy details.
- Use only the returned API information.
- Do not confuse product information with live availability.
- Clearly identify the information as simulated demo data.
- Do not claim to purchase or modify a product.
