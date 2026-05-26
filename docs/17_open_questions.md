# Open Design Questions

These questions should be answered before the first implementation pass.

## Product and Company Scope

1. What is the first insurance product line?
2. Is the target structure a carrier, MGA, captive, protocol, or architecture prototype?
3. What jurisdiction should the MVP model first?
4. Should the first product be admitted, surplus lines, parametric, captive, or a non-production sample product?
5. Should the system support direct-to-consumer only, or brokers and producers too?

## Blockchain Strategy

6. Should the MVP use public chain, permissioned EVM, appchain, or local-only EVM?
7. Should customers use wallets directly or should wallet abstraction hide blockchain details?
8. Should policies be registry records, NFTs, soulbound attestations, or another structure?
9. Should premiums support fiat only, stablecoin only, or both?
10. Should claim payouts support fiat only, stablecoin only, or both?
11. What testnet or local chain should be targeted first?
12. Should governance be traditional, on-chain, or hybrid?

## AI Agent Authority

13. Can the AI agent bind policies within strict rules, or only prepare bind requests?
14. Can the AI agent decline risks, or only refer them for human review?
15. Which actions always require licensed human approval?
16. Should customer communication include web chat, email, SMS, and voice?
17. What is the retention policy for AI conversation logs?

## Underwriting and Pricing

18. Should rating be deterministic rules first, ML first, or hybrid?
19. Which third-party data sources are permitted?
20. Which risk factors are prohibited?
21. Should underwriting be instant-bind or referral-heavy at launch?
22. How should manual overrides work?
23. Do we need adverse action notices in MVP?

## Risk Appetite

24. What is the initial maximum policy limit?
25. What is the maximum exposure per customer?
26. What is the maximum exposure per geography?
27. What target loss ratio should be modeled?
28. What concentration risks matter most?
29. Should growth or solvency protection be prioritized in ambiguous cases?
30. Should reinsurance be assumed from day one?

## Float and Treasury

31. Should float management be simulated only at first?
32. What assets are allowed for float?
33. Are stablecoins allowed at all?
34. What minimum liquidity percentage should be enforced?
35. What approval thresholds should apply to treasury actions?
36. Should the system integrate with a real custodian later?
37. Should investment yield influence quote pricing assumptions?

## Claims

38. Should claims be AI-assisted only or partially automated?
39. What claim types can be automatically paid?
40. What evidence types are required?
41. What fraud and abuse checks are required?
42. What payout thresholds require human review?
43. Should settlement support fiat, stablecoin, or customer choice?

## Data and Architecture

44. Should this remain a monorepo?
45. Should the first implementation be Python-first, TypeScript-first, or mixed?
46. Should Neo4j be included from day one?
47. Should Kafka or Redpanda be included immediately, or should MVP start with PostgreSQL outbox?
48. Should local dev use Docker Compose only at first?
49. Should cloud infrastructure be cloud-agnostic or target one provider?

## Compliance

50. Who are the intended users: consumers, licensed agents, internal staff, regulators, auditors, or all of these?
51. Should every material decision export into a review packet?
52. Should product/rate/form approval workflow be simulated or real from day one?
53. Should AI governance be implemented before AI can affect quote decisions?
54. What level of explainability is required for launch?
