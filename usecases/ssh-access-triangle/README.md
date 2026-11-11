# ssh-access-triangle: SSH only from the management network, on three switches

**Domains:** network · **Features:** `held-edit` `program-gate` `git-only` · access change

One change leg adds an SSH allowlist (`MGMT-SSH`: permit tcp/22 from `172.30.31.0/24`, deny and log the rest) to all three
switches of an OSPF triangle, as edits to their configuration files in this repository. Routing, interfaces and the HTTP API
are untouched.

**Released:** 2026-11-12 — the leg and the integration review approved: `MGMT-SSH` on all three switches, applied to SSH in the
default VRF, with the admitted network stated as taken from the spec.

**Git only.** The three-switch lab is not running, so there is no `git-live/` variant. The run needs no switches at all.

## Before you launch

- **Approvers are placeholders.** Replace each `…@example.com` approver with a person on your project's team list.
- **The management network is a choice, not a fact of your network.** `172.30.31.0/24` is the lab's management subnet. Use
  your own; a wrong range locks you out once the package is applied.
- You need only the pAIchart GitHub file source pinned to this repository (or your fork).

## What a successful run looks like

- One change leg with three Git file sources and no device service.
- Its package edits `network/igp-triangle/ceos{1,2,3}-startup.cfg`: an access list `MGMT-SSH` and its application to SSH in
  each VRF the files run SSH in, with a rollback, and a statement that the admitted network was taken from the spec, not
  observed.
- The integration review approves checks 1–3. You apply the package one switch at a time from inside the admitted network.
