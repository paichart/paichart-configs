# Give lab switch ceos2 one new telemetry-exporter loopback, on an address neither lab switch already uses

Two legs, one network fabric. It is deliberately small.

## What must happen

Lab switch ceos2 gets exactly one new loopback interface carrying one telemetry-exporter address (a single /32) from the
exporter pool `10.99.0.0/24`, and that address is advertised in BGP. Nothing else changes on ceos2, and nothing changes
on any other device.

Anything on the switches that this change does not touch is left as it is. A leg corrects nothing outside this change.

## Why this is a program and not one pipeline

The address is a value the change depends on. It is checked on its own, and approved, before any configuration is written
with it.

## Approval gates

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg types and the interface contract | the Program Architect | both legs | Plan Approver, plan.approver@example.com |
| address | the address Pipeline 1 published | Pipeline 1 publishing the address | Pipeline 2 | Address Approver, address.approver@example.com |
| network change | the change package Pipeline 2 produced for ceos2 | Pipeline 2 producing its change package | program completion only, not Pipeline 2's own work | Change Approver, change.approver@example.com |

The package is applied by a person after the network change gate. This run applies nothing.

## Pipeline 1 objective — exporter address (network-derivation, value)

Harvest ceos1 and ceos2 read-only from the sources its Device sources block declares, and derive one free exporter address
from `10.99.0.0/24`. Pipeline 1 applies these rules: an address is used by a lab switch when it lies inside any IPv4 prefix
configured on any interface of that switch, or inside any prefix that switch originates in BGP. An address is free when
neither ceos1 nor ceos2 uses it. Nothing outside the two switches is consulted. Of the free addresses, Pipeline 1 takes the
lowest, and never takes the pool's first or last address. Publish the address for the second leg. Pipeline 1 derives the
address and nothing else. Changes nothing.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
```

## Pipeline 2 objective — exporter loopback on ceos2 (network-provisioning, change) — depends on Pipeline 1

On ceos2, configure one new loopback with the address Pipeline 1 published, and advertise that address in BGP. Pipeline 2
uses that address and does not choose again.

Pipeline 2 chooses the loopback number: the lowest loopback number that is above every telemetry-exporter loopback any of
Pipeline 2's declared sources for ceos2 shows, and that none of those sources shows in use. The new loopback carries the same
description as the existing telemetry-exporter loopbacks on ceos2, and its address is advertised in BGP by the same mechanism
they use. Pipeline 2 states the number, the description and the mechanism it applied.

Pipeline 2 changes ceos2 only. ceos1 is listed so that Pipeline 2 sees it; nothing on ceos1 changes. Never applied by this run.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (4, 5, …).

1. Pipeline 2 configures on ceos2 exactly the address Pipeline 1 published.
2. That address is inside `10.99.0.0/24`, is not the pool's first or last address, and is not used by ceos1 or ceos2 as
   Pipeline 1 read them from its declared sources.
3. Pipeline 2 changes nothing beyond the one new loopback and its BGP advertisement on ceos2, and nothing on ceos1.

## Validation shape

Governed by each leg's own active protocol, not by this file. This document does not restate, weaken or override a
protocol clause.

## Connection surfaces

Both legs read the switches only through the platform's Git file source, from the files named in their Device sources
blocks. Neither leg reaches a running switch. `topology.json` declares no endpoint, category or tools of its own.
