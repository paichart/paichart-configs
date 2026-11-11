# Restrict SSH management access on the three triangle switches to the management network

One leg, three switches. It is deliberately small.

## What must happen

On each of ceos1, ceos2 and ceos3, SSH to the switch is accepted only from the management network `172.30.31.0/24`. SSH
from anywhere else is refused and logged. Nothing else changes on any switch: routing (OSPF), the interfaces, and the
switch's HTTP API stay as they are. Anything on the switches that this change does not touch is left as it is; the leg
corrects nothing outside this change.

## Why this is one leg

Every switch gets the same rule and no value passes between switches, so one leg changes all three.

## Approval gates

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg type and the interface contract | the Program Architect | Pipeline 1 | Plan Approver, plan.approver@example.com |
| access change | the change package for ceos1, ceos2 and ceos3 | Pipeline 1 producing its change package | program completion only, not Pipeline 1's own work | Access Approver, access.approver@example.com |

The package is applied by a person after the access change gate, one switch at a time, from a session inside
`172.30.31.0/24`. This run applies nothing.

## Pipeline 1 objective — SSH allowlist on ceos1, ceos2 and ceos3 (network-provisioning, change)

Pipeline 1 changes ceos1, ceos2 and ceos3, and applies these rules on each:

- The switch tells admitted sessions apart by their source address. Sessions reach the switch directly, with no address
  translation in between.
- What is protected is the SSH service of the switch, in every VRF the switch's configuration file runs SSH in. Pipeline 1
  states each VRF it covered.
- The admitted network may use SSH (tcp/22) only. The rule grants nothing else.
- Pipeline 1 creates an access list named `MGMT-SSH`: permit SSH from `172.30.31.0/24`, deny everything else with
  logging, and applies it to the SSH service. Any access list already applied to SSH is replaced by `MGMT-SSH`; Pipeline 1
  names each one it replaced.
- Other management services on the switch, including the HTTP API, are not touched.
- Pipeline 1 cannot confirm from configuration files that sessions arrive from `172.30.31.0/24`; it goes ahead, and states
  that the admitted network was taken from this file, not observed.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/igp-triangle/ceos1-startup.cfg
ceos2: git-file — service github-service ; paichart/paichart-configs/network/igp-triangle/ceos2-startup.cfg
ceos3: git-file — service github-service ; paichart/paichart-configs/network/igp-triangle/ceos3-startup.cfg
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (4, 5, …).

1. Each of ceos1, ceos2 and ceos3 gets an access list `MGMT-SSH` that permits tcp/22 from `172.30.31.0/24` only and denies
   everything else with logging.
2. On each switch that access list is applied to the SSH service in every VRF Pipeline 1 states SSH runs in.
3. Pipeline 1 changes nothing on any switch beyond that access list and its application to SSH.

## Validation shape

Governed by each leg's own active protocol, not by this file. This document does not restate, weaken or override a
protocol clause.

## Connection surfaces

Pipeline 1 reads the three switches only through the platform's Git file source, from the files named in its Device sources
block. It reaches no running switch. `topology.json` declares no endpoint, category or tools of its own.
