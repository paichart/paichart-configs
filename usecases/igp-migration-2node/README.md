# igp-migration-2node: OSPF to IS-IS in four gated phases

**Domains:** network · **Features:** `held-edit` `program-gate` `live-read` · routing change, human apply between legs

Four legs migrate a two-switch fabric (ceos1, ceos2, one point-to-point link) from OSPF to IS-IS without a routing outage:
add IS-IS beside OSPF, check IS-IS carries every OSPF route, make IS-IS preferred, remove OSPF. A person applies each phase
to the switches before releasing the next gate, and each leg reads the switches as that apply left them.

**Live only.** Each phase must see what the previous apply did to the running switches. A Git file is not updated by an
apply, so there is no `git-only/` variant: every switch is declared `device-read`, and the file each leg edits is the
running configuration it read.

## Before you launch

- **You need the switches running.** Two Arista EOS switches running OSPF (process 1, area 0.0.0.0) on one point-to-point
  link with a Loopback0 each (`network/igp-2node/` in this repository is the starting configuration), and a read-only device
  service. Point the Device sources lines and `readOnlyServices` at your own service's descriptor.
- **Approvers are placeholders.** Replace each `…@example.com` approver with a person on your project's team list. The
  migration approver applies each package before releasing its gate.
- **Choices written into the spec** (change them before launch if yours differ): instance name `CORE`; level 2 only; NET
  area `49.0001`; the preference switch is `distance 100` under the IS-IS IPv4 address family (below OSPF's 110).

## What a successful run looks like

- The plan gate shows four change legs in sequence, five gates.
- Pipeline 1's package adds the `CORE` instance on both switches in the EOS shape the spec gives; OSPF is untouched.
- After you apply it, Pipeline 2's report shows every OSPF prefix present in the IS-IS link-state database with a matching
  next hop (labelled derived), and the adjacency up. It makes no edit.
- Pipeline 3's package adds only `distance 100`; Pipeline 4's removes OSPF, with OSPF exactly as it read it as the rollback.
- The integration review approves checks 1–5. Every package is applied by you; the platform applies nothing.
