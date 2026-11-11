# Use cases

Each folder is a pAIchart **program** input: a `requirements.md` and a `topology.json` per variant, plus a README saying what must
be running, which values are placeholders and what success looks like. **Released** means a run came back
`programReleasable: true` — every leg approved and the program's integration reviewer approved.

Variants: `git-only/` reads only the files in this repository; `git-live/` also reads the running switches; `live/` reads only the
running switches. The two `requirements.md` files of a pair differ only in their Device sources blocks and "Connection surfaces"
(CI checks it).

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

## Prepared — network, not yet released

| Use case | Variants | What it does |
|---|---|---|
| [`igp-migration-2node`](igp-migration-2node/) | `live/` | OSPF to IS-IS in four gated phases; a person applies each phase before the next |
| [`held-network-window-p1`](held-network-window-p1/) | — | a loopback on each switch on a free address; its runs read an earlier repository and it has not run from this one |

## Pending — Kubernetes, Terraform, observability

Not the current focus. [`telemetry-export-held`](telemetry-export-held/) and [`held-terraform-window-p1`](held-terraform-window-p1/)
are here from earlier work; neither has run from this repository.

## Running one

Launch a `pov-program` task whose description names the variant's two raw URLs, for example:

```
Design artifacts for the Program Architect (fetch ONLY these two URLs):
- topology-as-code: https://raw.githubusercontent.com/paichart/paichart-configs/main/usecases/loopback-ceos2/git-only/topology.json
- requirements: https://raw.githubusercontent.com/paichart/paichart-configs/main/usecases/loopback-ceos2/git-only/requirements.md
```

The hub must be allowed to read this repository: `GIT_FILE_SOURCE_PIN=paichart/paichart-configs` (self-host run sheet step 9c).
A `git-live/` or `live/` variant also needs the read-only device service its topology names; without it a leg stops and says why.
