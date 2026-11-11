# igp-migration-2node-r18: OSPF to IS-IS in four gated phases

**Domains:** network · **Features:** `held-edit` `program-gate` `live-read` · routing change, human apply between legs

Four change legs migrate a two-switch fabric (ceos1, ceos2, one point-to-point link) from OSPF to IS-IS without a routing
outage: add IS-IS beside OSPF, check IS-IS carries every OSPF route, make IS-IS preferred, remove OSPF. A person applies each
phase to the switches before releasing the next gate, and each phase re-reads the switches as that apply left them.

**Where it comes from.** This is the specification of the 18th round of this migration (R18), which **released on 2026-08-28**
with all four legs approved. The text is R18's word for word, with three changes the current platform needs: each phase is its own
leg section; every leg declares where it reads the switches (a `## Device sources` block, `device-read` on both); the named approver
is a placeholder. It has not yet run from this repository. Its clauses are the result of seventeen earlier rounds — keep them.

**Live only.** Each phase must see what the previous apply did to the running switches, so every switch is declared
`device-read`; a Git file would go stale after the first apply.

## Before you launch

- **You need the switches running.** Two Arista EOS switches running OSPF (process 1, area 0.0.0.0) on one point-to-point link
  with a Loopback0 each (`network/igp-2node/` in this repository is the starting configuration), and a read-only device service.
  Point the Device sources lines at your own service's descriptor.
- **The approver is a placeholder.** Replace `migration.approver@example.com` with a person on your project's team list. That
  person applies each phase's package before releasing its gate.
- The planner derives the IS-IS design (NETs from the router IDs, metrics from the OSPF costs, the preference setting) in the
  plan you approve at the first gate.

## What a successful run looks like

- The plan gate shows four change legs in sequence and five gates; the contract carries the derived NETs, metrics and the
  canonical EOS stanza.
- Phase 1 adds IS-IS beside OSPF with OSPF untouched; phase 2 reports parity against the IS-IS link-state database, labelling
  derived next hops as derived; phase 3 adds the one preference setting; phase 4 removes OSPF, with OSPF exactly as it read it as
  the rollback.
- The integration review approves its checks. Every package is applied by you; the platform applies nothing.
