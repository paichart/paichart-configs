# loopback-ceos2: one new loopback, on an address no switch uses

**Domains:** network · **Features:** `derived-value` `cross-leg-value` `held-edit` `program-gate` · `git-only` or `live-read`

A value leg works out one free telemetry-exporter address from the pool `10.99.0.0/24` by reading both switches. A
change leg then adds one loopback on `ceos2` with that address and advertises it in BGP. The change leg edits `ceos2`'s
configuration file by reference; nothing is applied to a switch.

**Released:** the `git-only/` variant, 2026-11-11 — every leg and the integration review approved, with the address and
loopback described below. The `git-live/` variant has not been run yet.

## Pick a variant

| | [`git-only/`](git-only/) | [`git-live/`](git-live/) |
|---|---|---|
| Reads | the two configuration files in this repository | the same files, plus the running switches |
| You need | the pAIchart GitHub file source pinned to this repository | that, plus two switches running these files and a read-only device service |
| Limit | values are checked against the committed files only; the package says so | none beyond the spec |

The two `requirements.md` files are identical except for the `## Device sources` blocks and "Connection surfaces"
(checked by this repository's CI).

## Before you launch

- **Approvers are placeholders.** Replace each `…@example.com` approver in the gate table with a person on your project's
  team list in pAIchart (name and email). The program matches approvers by email.
- **git-live only:** the descriptor in `topology.json` points at the pAIchart lab's read-only switch service. On your own
  install, publish a descriptor for your own read-only service and change both the Device sources lines and
  `readOnlyServices` to its URL.
- Launch as a `pov-program` task whose description names this variant's raw `topology.json` and `requirements.md` URLs
  (see [`../README.md`](../README.md)).

## What a successful run looks like

- The plan gate shows two legs: a value leg and a change leg, with three gates.
- The value leg publishes one address inside `10.99.0.0/24`, not `.0` or `.255`, that neither switch uses. It changes
  nothing.
- The change leg's package adds one loopback on `ceos2` above the existing exporter loopbacks, with the same description and
  a BGP `network` statement, as edits to `network/base/ceos2-startup.cfg`, plus a rollback.
- The integration review approves checks 1–3, and the program completes releasable. You apply the package yourself after
  the network change gate.
