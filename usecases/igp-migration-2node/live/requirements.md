# Migrate the two-switch fabric from OSPF to IS-IS in four gated phases, with no routing outage

Four legs, in sequence, each spanning both switches (ceos1 and ceos2). A person applies each phase to the switches before
the next phase starts, and each phase reads the switches as they are after that apply.

## What must happen

ceos1 and ceos2 move from OSPF (process 1, area 0.0.0.0) to IS-IS, running both side by side until IS-IS is shown to carry
every route OSPF carries. The phases are: add IS-IS beside OSPF; check parity; make IS-IS preferred; remove OSPF.

Fixed for every leg:
- IS-IS instance `CORE` on both switches, level 2 only, address family IPv4 unicast.
- One NET per switch in area `49.0001`. Its system ID is the switch's OSPF router ID packed digit by digit: each of the four
  octets padded to three digits, the twelve digits regrouped in fours (router ID `10.0.0.1` gives `0100.0000.0001`).
- On each link, the IS-IS metric equals the OSPF cost that switch has on that link. Loopback0 is passive in IS-IS, as it is
  in OSPF.
- While both protocols run, OSPF-learned routes stay preferred on both switches. The switch to IS-IS is one setting:
  `distance 100` under `router isis CORE` → `address-family ipv4 unicast`; removing it switches back.

Nothing else changes: no interface addressing or descriptions, no new links, nothing on the management plane. Anything on the
switches that this migration does not touch is left as it is; a leg corrects nothing outside its phase.

## Why this is a program and not one pipeline

Each phase designs against the switches as a person left them after applying the previous phase. That state does not exist
until the apply, so no leg can be planned with it in advance.

## Approval gates

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg types and the interface contract | the Program Architect | all four legs | Plan Approver, plan.approver@example.com |
| G1 | Pipeline 1's package, applied by the approver before release | Pipeline 1 producing its change package | Pipeline 2 | Migration Approver, migration.approver@example.com |
| G2 | Pipeline 2's parity report | Pipeline 2 producing its report | Pipeline 3 | Migration Approver, migration.approver@example.com |
| G3 | Pipeline 3's package, applied by the approver before release | Pipeline 3 producing its change package | Pipeline 4 | Migration Approver, migration.approver@example.com |
| final | Pipeline 4's package, applied by the approver | Pipeline 4 producing its change package | program completion only, not Pipeline 4's own work | Migration Approver, migration.approver@example.com |

The platform applies nothing. Each phase's package is applied by the approver, in a configuration session, before its gate is
released.

## Platform dialect (every change leg)

Every candidate line is valid Arista EOS 4.32. Level 2 only is `is-type level-2`. EOS IS-IS uses wide metrics with no command
for it, so `metric-style` never appears. Passive is set per interface (`isis passive`), never `passive-interface` under
`router isis`. The IS-IS stanzas follow this shape, substituting only the bracketed values:

```
router isis CORE
   net <NET>
   is-type level-2
   !
   address-family ipv4 unicast
!
interface <Ethernet interface>
   isis enable CORE
   isis network point-to-point
   isis metric <value>
!
interface Loopback0
   isis enable CORE
   isis passive
```

## Pipeline 1 objective — add IS-IS beside OSPF on ceos1 and ceos2 (network-provisioning, change)

Pipeline 1 adds IS-IS on both switches by the fixed values above, on every interface that runs OSPF. The OSPF configuration
is not touched, and route preference is left so that OSPF-learned routes stay preferred. Its rollback removes the `CORE`
instance and the interface IS-IS lines.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Pipeline 2 objective — check IS-IS carries every OSPF route (network-provisioning, change) — depends on Pipeline 1

Pipeline 2 makes no edit to either switch and produces no change package. It first states whether Pipeline 1's IS-IS configuration is present on each
switch; a switch where its read does not show it is reported, and Pipeline 2 stops. Its deliverable is a parity report, per
switch: every prefix OSPF advertises with the next hop OSPF resolves for it, beside the same prefix in the IS-IS link-state
database with its IS-IS next hop, and the IS-IS adjacency on the link. A link-state database holds no resolved next hop, so
the IS-IS next hop is derived; Pipeline 2 labels it derived and names what it was derived from. A prefix missing from IS-IS,
or extra in it, is reported as a finding; the tolerance is zero. The comparison uses the link-state database, never the
routing table: while OSPF is preferred, IS-IS routes are not installed.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Pipeline 3 objective — make IS-IS preferred on ceos1 and ceos2 (network-provisioning, change) — depends on Pipeline 2

Pipeline 3 first states whether Pipeline 1's IS-IS configuration is present on each switch; a switch where its read does not
show it is reported, and Pipeline 3 stops. It then adds the one preference setting (`distance 100` under the IS-IS IPv4
address family) on both switches and nothing else. OSPF keeps running. Its rollback removes that setting.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Pipeline 4 objective — remove OSPF from ceos1 and ceos2 (network-provisioning, change) — depends on Pipeline 3

Pipeline 4 first states whether the preference setting is present on each switch; a switch where its read does not show it
is reported, and Pipeline 4 stops. It then removes the OSPF process and every interface OSPF line from both switches. Its
rollback is the OSPF configuration exactly as Pipeline 4 read it from each switch, copied, not rewritten.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (6, 7, …).

1. Every leg uses instance `CORE`, level 2 only, and the NETs and metrics the plan's contract states.
2. Each NET is in area `49.0001`, and its system ID is the packing of that switch's router ID (recompute it digit by digit).
3. Each interface's IS-IS metric equals the OSPF cost the leg read for that switch and link.
4. Each leg changes only its own phase: Pipeline 1 leaves OSPF and preference untouched; Pipeline 2 makes no edit;
   Pipeline 3 changes only the preference setting; Pipeline 4 removes only OSPF.
5. Pipeline 4's rollback is the OSPF configuration Pipeline 4 read, unchanged.

## Validation shape

Governed by each leg's own active protocol, not by this file. This document does not restate, weaken or override a
protocol clause.

## Connection surfaces

Every leg reaches the switches only through a self-provisioned read-only MCP service named by the descriptor URL in
`topology.json` `readOnlyServices`. No leg reads a Git file. `topology.json` declares no endpoint, category or tools of its own.
