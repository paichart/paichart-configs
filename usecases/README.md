# Use cases

Each folder is a pAIchart **program** input: a `requirements.md` and a `topology.json` per variant, plus a README saying what must
be running, which values are placeholders and what success looks like. **Released** means a run came back
`programReleasable: true` — every leg approved and the program's integration reviewer approved.

Variants: `git-only/` reads only the files in this repository; `git-live/` also reads the running switches; `live/` reads only the
running switches. The two `requirements.md` files of a pair differ only in their Device sources blocks and "Connection surfaces"
(CI checks it). A use case ships `git-only/` + `git-live/`; one whose values exist only in the running system (an address a
cluster assigns, a node's range) ships `live/` + `git-live/` instead, or `live/` alone, and its README says why.

## Released from this repository — network

| Use case | Shape | Released |
|---|---|---|
| [`loopback-ceos2`](loopback-ceos2/) | a value leg works out one free exporter address; a change leg adds a loopback on ceos2 with it | `git-only/` 2026-11-11, `git-live/` 2026-11-11 |
| [`firewall-partner-path-r2`](firewall-partner-path-r2/) | two change legs: the edge switch admits partner HTTPS and source-NATs it to a pool it selects and advertises; the core switch admits only that pool | `git-only/` 2026-11-11, `git-live/` 2026-11-12 |
| [`ssh-access-triangle`](ssh-access-triangle/) | one change leg adds an SSH allowlist for the management network on three switches | `git-only/` 2026-11-12 |

### What each run proved

**`loopback-ceos2`**
- The address the value leg works out from the running switches matches the one it works out from the files alone
  (`10.99.0.3/32` both times), so the files here reflect what the switches hold.
- The change leg read ceos2 from Git and from the device. Where the file differs from the running switch, the package said so and
  applies only the added lines, never the whole file.
- Each rule sat with the leg that applies it: the value leg chose the address, the change leg chose the loopback number, its
  description and how it is advertised.

**`firewall-partner-path-r2`**
- A value can pass between two change legs: the edge leg chose the NAT pool (`10.99.0.6/31`), the core leg used exactly that pool.
- The same design comes out whether the legs read Git only or Git and the running switches.
- Applied on a lab pair of switches (core first, then edge, on a commit timer) and rolled back: every line was accepted, the core
  switch learned the pool from the edge over BGP, the BGP session stayed up. Not shown yet: NAT translating real partner traffic
  end to end (the lab has no partner or app hosts).
- [`firewall-partner-path`](firewall-partner-path/) is its first revision. Its run was correctly refused by the integration
  reviewer: the core rule sat on an interface the traffic never crosses, and nothing routed the replies back to the pool.

**`ssh-access-triangle`**
- The first run of an access change: every choice in the spec — who is admitted, which service, what happens to existing access
  lists, what stays untouched — reached the change package.
- One leg changed three switches the same way, from their files alone.
- The stanza was accepted by the switch software in a configuration session (then discarded). Not shown yet: SSH refused on a
  running switch (the three-switch lab is not running).

## Released from this repository — Terraform

| Use case | Shape | Released |
|---|---|---|
| [`terraform-archive-owner-tag`](terraform-archive-owner-tag/) | one change leg adds an owner tag to the archive bucket, as an edit to `terraform/archive.tf` | `git-only/` 2026-11-19, `git-live/` 2026-11-19 |

### What the run proved

**`terraform-archive-owner-tag`**
- The first run on terraform-iac 1.17.0: the leg read only the file its `## Config sources` block declares, and the package is one
  edit to that file that adds the `owner` line and leaves `team` and `tier` as the file gives them.
- The package carries a `Plan witness`: the resource, "update in place" and the one key the change sets, with the sentence that
  tells the person applying it to stop if the team's CI plan shows anything else. The platform checked the witness against the
  edit itself (the sentence word for word, nothing missing, no unchanged key given a value) before the review.
- pAIchart computed no drift and ran no plan; on `git-only/` the package says it was designed against the `.tf` file only.
- The `git-live/` run also read the Terraform state of the `prod` workspace, through the read-only Terraform service the platform
  set up from the declared line. The state was reported beside the file, as evidence, and nobody compared the two: the team's CI
  plan remains the check. The package makes the same one-line change as on `git-only/`.

## Released from this repository — observability

| Use case | Shape | Released |
|---|---|---|
| [`otlp-ingress-three-leg`](otlp-ingress-three-leg/) | a network value leg works out the exporter range; three observability legs each change one file from one shared `## Config sources` block: the OTLP ingress admits only that range, the collector's batch processor gets two settings, the operator listener a larger body size | `git-live/` 2026-11-25 |

### What the run proved

**`otlp-ingress-three-leg`**
- Three legs of one protocol shared one declared block: each leg read and kept every declared file, and each changed only its own.
  Only the operator leg touched the body-size setting both nginx files carry.
- The platform compared each Git file with its served copy (identical, all three) and showed the result to the designer and the
  reviewer; nobody had to compare by hand.
- With two observability legs or more the spec names a read-only service registered once before launch, so no leg removes it
  under another (see the use case's README).
- Its first run was refused because one leg's brief narrowed what its Harvester read; the platform's read rule, placed beside the
  block, fixed it, and the re-run released. Nothing was applied.

## Released from this repository — four domains in one program

| Use case | Shape | Released |
|---|---|---|
| [`telemetry-export-held-r3`](telemetry-export-held-r3/) | a network value leg works out the telemetry exporter range; a Kubernetes, a Terraform and an observability change leg each admit only that range | `git-live/` 2026-11-19 |

### What the run proved

**`telemetry-export-held-r3`**
- One value crossed three domain boundaries unchanged: the network leg worked out `10.99.0.0/27` from six exporter addresses on the
  two switches, and the NetworkPolicy, the bucket policy and the OTLP sender restriction each admit exactly that range.
- Each change is an edit to the file the team keeps in Git where one is declared; the live cluster, Terraform state and running
  stack were read as evidence.
- Each domain's own platform check ran: the Kubernetes file was compared with the live cluster (no differences); the Terraform
  package's Plan witness was checked against its edit (pAIchart computes no Terraform drift; the team's CI plan is the check); the
  network derivation was checked against the harvested addresses.
- Five gates, each released by a person: the plan, the exporter range, and one per change package. Nothing was applied.

## Prepared — network, not yet released

| Use case | Variants | What it does |
|---|---|---|
| [`igp-migration-2node-r18`](igp-migration-2node-r18/) | `live/` | OSPF to IS-IS in four gated phases; a person applies each phase before the next. R18's specification (released 2026-08-28), updated only for the current platform |

## Pending — Kubernetes, Terraform, observability

[`telemetry-export-net-k8s-r2`](telemetry-export-net-k8s-r2/) — the same program as `git-only/` and `git-live/` twins. Not yet run.

[`telemetry-export-net-k8s`](telemetry-export-net-k8s/) — a network value leg works out the telemetry exporter range; a Kubernetes change leg admits only that range to the receiver. Written by hand with the spec checklist; Kubernetes reads Git and the live cluster. Not yet run.

Earlier revisions, kept as their runs' inputs: [`telemetry-export-held-r2`](telemetry-export-held-r2/), [`telemetry-export-held`](telemetry-export-held/) and [`held-terraform-window-p1`](held-terraform-window-p1/).
None has run from this repository, and none runs to completion today: from terraform-iac 1.17.0 a Terraform leg with no
`## Config sources` block stops before it reads anything (and from kubernetes-gitops 1.19.0 so does a Kubernetes leg). Use
[`telemetry-export-held-r3`](telemetry-export-held-r3/) and [`terraform-archive-owner-tag`](terraform-archive-owner-tag/) instead.

## Running one

Launch a `pov-program` task whose description names the variant's two raw URLs, for example:

```
Design artifacts for the Program Architect (fetch ONLY these two URLs):
- topology-as-code: https://raw.githubusercontent.com/paichart/paichart-configs/main/usecases/loopback-ceos2/git-only/topology.json
- requirements: https://raw.githubusercontent.com/paichart/paichart-configs/main/usecases/loopback-ceos2/git-only/requirements.md
```

The hub must be allowed to read this repository: `GIT_FILE_SOURCE_PIN=paichart/paichart-configs` (self-host run sheet step 9c).
A `git-live/` or `live/` variant also needs the read-only device service its topology names; without it a leg stops and says why.
