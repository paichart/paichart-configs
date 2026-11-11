# Let a partner reach an internal app over HTTPS, source-NATed at the edge switch and admitted at the core switch

Two legs on one network fabric, in sequence along the traffic path: partner → ceos1 (edge, `Ethernet3` in, `Ethernet1` out)
→ fabric link → ceos2 (core, `Ethernet1` in) → app.

## What must happen

Partner traffic from `203.0.113.0/24` reaches the internal app `10.20.0.10/32` on tcp/443 and nothing else. On ceos1 the
partner source is translated to a NAT pool taken from free addresses in `10.99.0.0/24`, and ceos1 advertises that pool to
ceos2 so the app's replies route back to ceos1. ceos2 admits traffic to the app from that pool only, never from the partner
range. Every rule carries the tag `PARTNER-HTTPS-2026`; the NAT pool carries the tag `PARTNER-SNAT-2026`.

ceos1 is AS 65001 and ceos2 is AS 65002, joined by the `10.0.12.0/30` link (ceos1 `Ethernet1` `10.0.12.1`, ceos2 `Ethernet1`
`10.0.12.2`). That eBGP session and every route it carries today stay as they are; the only routing change is ceos1
advertising the NAT pool. Nothing else changes on either switch. Anything on the switches that this change does not touch is
left as it is; a leg corrects nothing outside this change.

**Reachability.** After the change, ceos2 holds a route to the NAT pool learned from ceos1 over BGP, and the BGP session and
the routes it carries today are unchanged. How the app's own address is reached beyond ceos2 is outside this program: it is
provided by routing this program does not change.

## Why this is a program and not one pipeline

The NAT pool is chosen by the edge leg from addresses that are free when it runs. The core leg needs that exact pool, and it
does not exist until the edge leg has chosen it.

## Approval gates

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg types and the interface contract | the Program Architect | both legs | Plan Approver, plan.approver@example.com |
| edge change | the ceos1 change package, including the NAT pool and its advertisement | Pipeline 1 producing its change package | Pipeline 2 | Edge Approver, edge.approver@example.com |
| core change | the ceos2 change package | Pipeline 2 producing its change package | program completion only, not Pipeline 2's own work | Core Approver, core.approver@example.com |

The packages are applied by a person after both change gates, core first and edge last, so partner traffic is never
admitted toward a hop that cannot yet police it. This run applies nothing.

## Pipeline 1 objective — edge policy, NAT pool and its advertisement on ceos1 (network-provisioning, change)

Pipeline 1 changes ceos1 only. It reads ceos1 and ceos2 from the sources its Device sources block declares; ceos2 is read
so that its allocations are seen, and nothing on ceos2 changes.

- Pipeline 1 binds the partner ingress rule inbound on `Ethernet3` (description `PARTNER-UPLINK`) on ceos1. The rule permits
  exactly tcp/443 from `203.0.113.0/24` to `10.20.0.10/32`, then denies everything else with logging.
- Pipeline 1 selects the NAT pool: the smallest aligned block (a /31, or a /30 only when no /31 is free) inside
  `10.99.0.0/24` in which no address is used by ceos1 or ceos2. An address is used when it lies inside any prefix configured
  on an interface of either switch or any prefix either switch originates in BGP. Pipeline 1 publishes the pool and the
  candidates it ruled out.
- Pipeline 1 translates `203.0.113.0/24` to that pool for traffic leaving ceos1 toward ceos2 on `Ethernet1`. Every list that
  selects traffic for the translation carries the same destination and port bounds as the ingress rule: tcp,
  `10.20.0.10/32`, port 443.
- Pipeline 1 makes ceos1 advertise exactly the pool to ceos2 in BGP AS 65001: one static route for the pool to `Null0` and
  one `network` statement for the pool, beside the existing ones. No other BGP setting changes.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Pipeline 2 objective — core policy on ceos2 (network-provisioning, change) — depends on Pipeline 1

Pipeline 2 changes ceos2 only. It reads ceos1 and ceos2 from the sources its Device sources block declares; nothing on ceos1
changes.

- Pipeline 2 binds a rule inbound on `Ethernet1` (description `to-ceos1`), where traffic from ceos1 arrives on ceos2. The rule
  permits tcp/443 from the NAT pool Pipeline 1 published to `10.20.0.10/32`, then denies with logging every other packet
  addressed to `10.20.0.10/32`, then permits all other traffic, so the BGP session and the routes it carries are not
  affected. Pipeline 2 uses the pool as published and does not choose or recompute it.
- No rule on ceos2 matches `203.0.113.0/24`. Pipeline 2 adds no route and no BGP setting: ceos2 learns the pool from
  ceos1.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (8, 9, …).

1. The pool ceos2 admits is exactly the pool Pipeline 1 published.
2. Every address in that pool is inside `10.99.0.0/24` and is used by neither switch as Pipeline 1 read them.
3. The pool is aligned and is a /31, or a /30 with no free aligned /31 in `10.99.0.0/24`.
4. No entry on either switch permits traffic to `10.20.0.10/32` beyond tcp/443 from its hop's source (`203.0.113.0/24` on
   ceos1, the pool on ceos2), and every list that selects traffic for the translation carries those bounds.
5. `203.0.113.0/24` appears in rules on ceos1 only.
6. The program deliverable states the design order (edge, then core) and the apply order (core, then edge).
7. ceos1's package adds exactly one static route and one BGP `network` statement, both for the pool, and changes no other
   BGP setting; ceos2's package adds no route and no BGP setting.

## Validation shape

Governed by each leg's own active protocol, not by this file. This document does not restate, weaken or override a
protocol clause.

## Connection surfaces

Both legs read the switches' configuration files through the platform's Git file source, and reach the running switches
only through a self-provisioned read-only MCP service named by the descriptor URL in `topology.json` `readOnlyServices`.
`topology.json` declares no endpoint, category or tools of its own.
