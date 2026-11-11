# firewall-partner-path-r2: partner HTTPS through two switches, source-NATed at the edge

**Domains:** network · **Features:** `derived-value` `cross-leg-value` `held-edit` `program-gate` · `git-only` or `live-read`

An edge leg on `ceos1` permits partner HTTPS from `203.0.113.0/24` to the app `10.20.0.10/32`, translates the partner source
to a NAT pool it selects from free addresses in `10.99.0.0/24`, and advertises that pool to `ceos2` in BGP. A core leg on
`ceos2` admits traffic to the app from exactly that pool. Both legs share one Device sources list: each edits only its own
switch's file and reads the other switch as evidence.

**Revision 2** of [`firewall-partner-path`](../firewall-partner-path/). The first revision's integration review refused it
on two plan defects: the core rule sat on an interface the traffic never crosses, and nothing routed the app's replies back
to the NAT pool. This revision binds the core rule where traffic from ceos1 arrives (`Ethernet1`), has ceos1 advertise the
pool, states what must be reachable, and keeps the BGP session safe (the core rule denies other traffic to the app only).

## Pick a variant

| | [`git-only/`](git-only/) | [`git-live/`](git-live/) |
|---|---|---|
| Reads | the two configuration files in this repository | the same files, plus the running switches |
| You need | the pAIchart GitHub file source pinned to this repository | that, plus two switches running these files and a read-only device service |
| Limit | the pool is checked against the committed files only; the package says so | none beyond the spec |

## Before you launch

- **Approvers are placeholders.** Replace each `…@example.com` approver with a person on your project's team list.
- **git-live only:** point the Device sources lines and `readOnlyServices` at your own read-only device service's descriptor.
- Launch as a `pov-program` task naming this variant's raw `topology.json` and `requirements.md` URLs, in a project that is
  not marked as a demo (a demo project does not show the switch files to the change author).

## What a successful run looks like

- Two change legs in sequence; the core leg waits for the edge leg and the edge gate.
- The edge package: an ingress rule on `Ethernet3`, a /31 (or a /30 only when no /31 is free) NAT pool neither switch uses,
  a translation whose match list is no wider than tcp/443 to the app, a static route and a BGP `network` statement for the
  pool, and the two tags.
- The core package: a rule inbound on `Ethernet1` admitting the pool to the app on tcp/443, denying and logging other
  traffic to the app, and passing everything else; no rule matching the partner range; no routing change.
- The integration review approves checks 1–7, including both orders: design edge → core, apply core → edge.
