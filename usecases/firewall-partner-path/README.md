# firewall-partner-path: partner HTTPS through two switches, source-NATed at the edge

> **Superseded by [`firewall-partner-path-r2`](../firewall-partner-path-r2/).** Its git-only run (2026-11-11) was refused at
> the integration review on two plan defects: the core rule sat on `Ethernet2`, which traffic from ceos1 never crosses, and no
> route took the app's replies back to the NAT pool. Kept unchanged as that run's input.

**Domains:** network · **Features:** `derived-value` `cross-leg-value` `held-edit` `program-gate` · `git-only` or `live-read`

An edge leg on `ceos1` permits partner HTTPS from `203.0.113.0/24` to the app `10.20.0.10/32` and translates the partner
source to a NAT pool it selects from free addresses in `10.99.0.0/24`. A core leg on `ceos2` admits exactly that pool. Both
legs share one Device sources list: each edits only its own switch's file and reads the other switch as evidence.

Cut down from a three-domain program (edge switch, cloud security group, core switch) that released on 2026-09-18; this
version keeps the two network legs.

## Pick a variant

| | [`git-only/`](git-only/) | [`git-live/`](git-live/) |
|---|---|---|
| Reads | the two configuration files in this repository | the same files, plus the running switches |
| You need | the pAIchart GitHub file source pinned to this repository | that, plus two switches running these files and a read-only device service |
| Limit | the pool is checked against the committed files only; the package says so | none beyond the spec |

The two `requirements.md` files are identical except for the `## Device sources` blocks and "Connection surfaces"
(checked by this repository's CI).

## Before you launch

- **Approvers are placeholders.** Replace each `…@example.com` approver with a person on your project's team list (name and
  email).
- **git-live only:** point the Device sources lines and `readOnlyServices` at your own read-only device service's descriptor.
- Launch as a `pov-program` task naming this variant's raw `topology.json` and `requirements.md` URLs.

## What a successful run looks like

- Two change legs in sequence; the core leg waits for the edge leg and the edge gate.
- The edge package: an ingress rule on `Ethernet3`, a /31 (or a /30 only when no /31 is free) NAT pool that neither switch
  uses, a translation whose match list is no wider than tcp/443 to the app, deny-and-log, and the two tags.
- The core package: a rule on `Ethernet2` admitting exactly that pool, no rule matching the partner range.
- The integration review approves checks 1–6, including both orders: design edge → core, apply core → edge.
