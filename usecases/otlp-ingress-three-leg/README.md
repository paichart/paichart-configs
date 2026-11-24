# otlp-ingress-three-leg

One value worked out on the network, used by one of three observability legs. A network value leg works out the telemetry
exporter range from the two lab switches. Three observability legs then each change ONE file of the observability stack:

| Leg | File it changes | Change | Uses the range |
|---|---|---|---|
| Pipeline 2 — ingress | `observability/nginx/otlp-ingress.conf` | sender restriction on TCP 4317 and TCP 4318: only the exporter range is admitted | yes, the only leg that does |
| Pipeline 3 — collector | `observability/otelcol/config.yaml` | the `batch` processor gets `send_batch_size: 8192` and `timeout: 5s` | no |
| Pipeline 4 — operator | `observability/nginx/operator-access.conf` | `client_max_body_size` on the TCP 14318 listener from `16m` to `32m` | no |

All three observability legs declare the SAME `## Config sources` block, naming all three files, because every leg of one
protocol reads and holds every `git-file` line of that protocol's block. Each leg edits only its own file.

Both nginx files carry `client_max_body_size 16m;` (the ingress file on TCP 4318, the operator file on TCP 14318). Only the
operator leg changes it, and only in `operator-access.conf`; the spec says so in the scope, in both legs and in Node C check 7.

Built from [`telemetry-export-held-r3`](../telemetry-export-held-r3/) `git-live/` (its network value leg and its observability
design decisions), with the Kubernetes and Terraform legs removed and the observability leg split in three. Details: each variant's
`PROVENANCE.md`.

**Needs observability-config 1.12.0** (not yet deployed when this was written). Under an earlier version an observability leg
does not read a `## Config sources` block. This use case is the input for the 1.12.0 canary.

**Variants:** `git-live/` only. There is no `git-only/` variant: every observability leg reads the running stack's state
(targets and rules) through the read-only observability service, whatever its Config sources block declares. With three
observability legs that service must be pre-registered and named by its registered name, and only a `live-read` line can name
it, so the observability files cannot be Git-only. (A descriptor URL instead would let each leg register the service and delete
it at its end, under a leg still running.)

**What must be running:** the lab switches ceos1 and ceos2 behind the read-only switch service, and the lab observability stack
behind the read-only observability service (descriptor URLs in `git-live/topology.json`), plus the pAIchart GitHub file source
pinned to this repository.

## Before you launch

- **Approvers** are the pAIchart lab team, as in r3: Josh Allen (plan), Steve Terry (exporter value), Jacob Wilcox (the three
  observability change gates). On your own install, replace each with a person on your project's team list (name and email).
- **Setup step: register the read-only observability service once, before launching.** This program has three
  observability legs, so their lines name the service by its registered name, `observability-readonly`, never by a descriptor
  URL. With a URL each leg would register the service itself and delete its own registration when it ends, so the first leg to
  finish would remove the service under a leg still running. As the launching account:
  1. Check that no older registration named `observability-readonly` exists (`registry(action:'list')`); remove a stale one
     first.
  2. Register it once from its descriptor URL:
     `registry(action:'register', descriptorUrl:'https://raw.githubusercontent.com/paichart/paichart/main/descriptors/observability-readonly-descriptor.json')`.
  3. Leave it registered for the whole run; no leg registers, updates or deletes it. Remove it yourself after the program ends.

  The switch service is registered by the value leg from its descriptor URL, as in `loopback-ceos2`.
- The exporter addresses in `network/base/ceos*-startup.cfg` are regenerated when the lab is rebuilt; the value leg reads both
  the files and the running switches.
- Launch as a `pov-program` task whose description names the variant's raw `topology.json` and `requirements.md` URLs (see
  [`../README.md`](../README.md)).

## What a successful run looks like

- The plan gate shows four legs and six gates: the plan, the exporter value (before the ingress leg only), and one change gate
  after each observability leg. The collector and operator legs depend on no other leg.
- The value leg publishes the smallest aligned range covering the six exporter-marked loopback addresses of ceos1 and ceos2. It
  changes nothing.
- The ingress package admits exactly that range on TCP 4317 and TCP 4318 in `otlp-ingress.conf` and leaves that file's
  `client_max_body_size` line as it is. The collector package sets the two keys of the `batch` processor and nothing else. The
  operator package changes one line of `operator-access.conf`. Each is an edit to the held Git file, with a rollback.
- The integration review approves checks 1–8, and the program completes releasable. Nothing is applied.

**Not yet run.**
