# Let a partner reach an internal app over HTTPS, source-NATed at the edge switch and admitted at the core switch

Two legs on one network fabric, in sequence along the traffic path: partner → ceos1 (edge) → ceos2 (core) → app.

## What must happen

Partner traffic from `203.0.113.0/24` reaches the internal app `10.20.0.10/32` on tcp/443 and nothing else. On ceos1 the
partner source is translated to a NAT pool taken from free addresses in `10.99.0.0/24`; ceos2 admits that pool, never the
partner range. Every rule carries the tag `PARTNER-HTTPS-2026`; the NAT pool carries the tag `PARTNER-SNAT-2026`. Each hop
denies everything else and logs the denies.

The eBGP fabric between the switches (the `10.0.12.0/30` link, AS 65001 and 65002) does not change. Nothing else changes on
either switch. Anything on the switches that this change does not touch is left as it is; a leg corrects nothing outside
this change.

## Why this is a program and not one pipeline

The NAT pool is chosen by the edge leg from addresses that are free when it runs. The core leg needs that exact pool, and it
does not exist until the edge leg has chosen it.

## Approval gates

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg types and the interface contract | the Program Architect | both legs | Plan Approver, plan.approver@example.com |
| edge change | the ceos1 change package, including the NAT pool | Pipeline 1 producing its change package | Pipeline 2 | Edge Approver, edge.approver@example.com |
| core change | the ceos2 change package | Pipeline 2 producing its change package | program completion only, not Pipeline 2's own work | Core Approver, core.approver@example.com |

The packages are applied by a person after both change gates, core first and edge last, so partner traffic is never
admitted toward a hop that cannot yet police it. This run applies nothing.

## Pipeline 1 objective — edge policy and NAT pool on ceos1 (network-provisioning, change)

Pipeline 1 changes ceos1 only. It reads ceos1 and ceos2 from the sources its Device sources block declares; ceos2 is read
so that its allocations are seen, and nothing on ceos2 changes.

- Pipeline 1 binds the partner ingress rule to `Ethernet3` (description `PARTNER-UPLINK`) on ceos1. The rule permits exactly
  tcp/443 from `203.0.113.0/24` to `10.20.0.10/32`, then denies everything else with logging.
- Pipeline 1 selects the NAT pool: the smallest aligned block (a /31, or a /30 only when no /31 is free) inside
  `10.99.0.0/24` in which no address is used by ceos1 or ceos2. An address is used when it lies inside any prefix configured
  on an interface of either switch or any prefix either switch originates in BGP. Pipeline 1 publishes the pool and the
  candidates it ruled out.
- Pipeline 1 translates `203.0.113.0/24` to that pool. Every list that selects traffic for the translation carries the same
  destination and port bounds as the ingress rule: tcp, `10.20.0.10/32`, port 443.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
```

## Pipeline 2 objective — core policy on ceos2 (network-provisioning, change) — depends on Pipeline 1

Pipeline 2 changes ceos2 only. It reads ceos1 and ceos2 from the sources its Device sources block declares; nothing on ceos1
changes.

- Pipeline 2 binds a rule to `Ethernet2` (description `DMZ-SEGMENT`) on ceos2 that permits exactly tcp/443 from the NAT pool
  Pipeline 1 published to `10.20.0.10/32`, then denies everything else with logging. Pipeline 2 uses that pool as published
  and does not choose or recompute it.
- No rule on ceos2 matches `203.0.113.0/24`.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (7, 8, …).

1. The pool ceos2 admits is exactly the pool Pipeline 1 published.
2. Every address in that pool is inside `10.99.0.0/24` and is used by neither switch as Pipeline 1 read them.
3. The pool is aligned and is a /31, or a /30 with no free aligned /31 in `10.99.0.0/24`.
4. No list on either switch that selects this traffic is wider than tcp/443 to `10.20.0.10/32` from its hop's source
   (`203.0.113.0/24` on ceos1, the pool on ceos2).
5. `203.0.113.0/24` appears in rules on ceos1 only.
6. The program deliverable states the design order (edge, then core) and the apply order (core, then edge).

## Validation shape

Governed by each leg's own active protocol, not by this file. This document does not restate, weaken or override a
protocol clause.

## Connection surfaces

Both legs read the switches only through the platform's Git file source, from the files named in the Device sources
block. Neither leg reaches a running switch. `topology.json` declares no endpoint, category or tools of its own.
