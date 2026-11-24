# Program Requirements — OTLP Ingress, Collector and Operator Listener, Three Observability Legs (kept files)

One value worked out on the network, used by one of three observability legs: a network value leg works out the telemetry exporter
range; an observability leg restricts the OTLP ingress to that range; two more observability legs each make one unrelated change to
one other file of the same stack.

---

## Program scope

- **4 legs** (pipelines). Each leg is a distinct change — never a device split and never a tidiness split:
  1. **Network derivation (fabric)** (UPSTREAM, **value leg**) on the fabric devices ceos1 and ceos2, described in `topology.json` `fabric`.
  2. **OTLP ingress sender restriction** (observability-config, change; DOWNSTREAM of Pipeline 1) on the OTLP ingress declared in Design decisions row `observability-config.ingress.target`, as a change to the file `observability/nginx/otlp-ingress.conf` only.
  3. **Collector batch processor** (observability-config, change; depends on no other leg) on the processor declared in row `observability-config.collector.target`, as a change to the file `observability/otelcol/config.yaml` only.
  4. **Operator listener body size** (observability-config, change; depends on no other leg) on the listener declared in row `observability-config.operator.target`, as a change to the file `observability/nginx/operator-access.conf` only.
- **Applying any of the three produced change packages is explicitly out of scope** — this program produces approved change packages only. Any file, listener, processor or setting other than the three declared targets above is explicitly out of scope.
- 🔴 **Two files carry the same directive, and only one leg changes it.** `observability/nginx/otlp-ingress.conf` (the TCP 4318 listener) and `observability/nginx/operator-access.conf` (the TCP 14318 listener) each carry the line `client_max_body_size 16m;`. **Only Pipeline 4 changes `client_max_body_size`, and only in `observability/nginx/operator-access.conf`.** Pipeline 2 leaves the `client_max_body_size` line of `observability/nginx/otlp-ingress.conf` exactly as the file gives it. Pipeline 3 touches neither nginx file.

## Design decisions

### Every leg

| id | question | options | rule or named target | source |
|---|---|---|---|---|
| network-derivation.target | which surface of the leg's service does it act on | — | every interface, on ceos1 and ceos2, whose description carries the exporter marker | (declared — r3 item 5: "the fabric's exporter addresses are the IPv4 addresses of interfaces whose description marks them as telemetry exporters") |
| network-derivation.population | which members of the class the derivation reads | — | interfaces whose description carries the exporter marker; no other fabric address qualifies | (declared — r3 item 5: "No other fabric address is an exporter address. The fabric leg reports, in its own deliverable, the description marker it applied.") |
| network-derivation.representation | how the derived value is expressed | one aligned prefix · a set of prefixes · a host list | the smallest CIDR block, aligned to a valid prefix boundary, containing every exporter address | (declared — r3 item 6: "the fabric leg computes the smallest CIDR block, aligned to a valid prefix boundary, that contains every one of the fabric's exporter addresses") |
| network-derivation.inputs-empty | the derivation's inputs are empty | gap | report a gap naming that no interface anywhere in scope carries the marker; publish nothing | (forced — r3 item 5: "No other fabric address is an exporter address") → gap — a substitute population is outside the declared marker rule |
| observability-config.ingress.target | which surface the ingress leg acts on | — | the observability stack's OTLP ingress, on TCP 4317 and TCP 4318, as configured in `observability/nginx/otlp-ingress.conf` | (declared — r3 item 4: "the observability stack's OTLP ingress in front of the collector, on TCP 4317 (OTLP gRPC) and TCP 4318 (OTLP HTTP)"; the file: owner 2026-11-24) |
| observability-config.collector.target | which surface the collector leg acts on | — | the `batch` processor declared under `processors:` in `observability/otelcol/config.yaml` | (declared — owner 2026-11-24: "in `observability/otelcol/config.yaml`, set the batch processor") |
| observability-config.operator.target | which surface the operator leg acts on | — | the `client_max_body_size` directive of the TCP 14318 listener in `observability/nginx/operator-access.conf` | (declared — owner 2026-11-24: "in `observability/nginx/operator-access.conf`, raise `client_max_body_size` on the TCP 14318 listener") |
| observability-config.files | which files each observability leg may change | — | each observability leg changes ONLY its own target's file (ingress: `observability/nginx/otlp-ingress.conf`; collector: `observability/otelcol/config.yaml`; operator: `observability/nginx/operator-access.conf`) and makes no edit to the other two, which it reads and holds because the shared Config sources block declares them | (declared — owner 2026-11-24: "three observability-config CHANGE legs, each changing ONE file, all three declaring the SAME `## Config sources` block") |
| approver.program-plan | who approves this gate | — | Josh Allen, josh.allen@paichart.com | (declared — r3 item 7: "program plan - Josh Allen (josh.allen@paichart.com)") |
| approver.fabric-exporter-value | who approves this gate | — | Steve Terry, steve.terry@paichart.com | (declared — r3 item 7: "fabric exporter value (network-provisioning) - Steve Terry (steve.terry@paichart.com)") |
| approver.ingress-change-method | who approves this gate | — | Jacob Wilcox, jacob.wilcox@paichart.com | (declared — r3 item 7: "observability change method (observability-config) - Jacob Wilcox (jacob.wilcox@paichart.com)"; one gate per observability leg: owner 2026-11-24) |
| approver.collector-change-method | who approves this gate | — | Jacob Wilcox, jacob.wilcox@paichart.com | (declared — owner 2026-11-24: one observability change-method gate per observability leg, approver Jacob Wilcox as in r3) |
| approver.operator-change-method | who approves this gate | — | Jacob Wilcox, jacob.wilcox@paichart.com | (declared — owner 2026-11-24: one observability change-method gate per observability leg, approver Jacob Wilcox as in r3) |
| gate.fabric-exporter-value.position | when this gate sits | before-leg · after-leg-before-completion · after-producer-before-consumers | after-producer-before-consumers: after Pipeline 1, before Pipeline 2 | (declared — r3 item 8: "the fabric exporter value gate sits after the fabric leg and before the … consuming legs"; Pipeline 2 is the only consuming leg: owner 2026-11-24) |
| gate.ingress-change-method.position | when this gate sits | before-leg · after-leg-before-completion · after-producer-before-consumers | after-leg-before-completion | (declared — r3 item 8: "sits AFTER its own leg and approves that leg's produced change package before the program completes; it does not block the leg's authoring") |
| gate.collector-change-method.position | when this gate sits | before-leg · after-leg-before-completion · after-producer-before-consumers | after-leg-before-completion | (declared — r3 item 8, as above; owner 2026-11-24) |
| gate.operator-change-method.position | when this gate sits | before-leg · after-leg-before-completion · after-producer-before-consumers | after-leg-before-completion | (declared — r3 item 8, as above; owner 2026-11-24) |

### A leg that grants or removes access (authorisation) — observability-config, ingress leg (Pipeline 2)

| id | question | options | rule or named target | source |
|---|---|---|---|---|
| observability-config.ingress.receiver | which workload/resource on the target is authorised | — | the OTLP ingress on TCP 4317 and TCP 4318 only | (declared — r3 item 4: "on TCP 4317 (OTLP gRPC) and TCP 4318 (OTLP HTTP)") |
| observability-config.ingress.admitted-principal | who is admitted, and by which attribute | source-address-range · named-identity · network-path · combination | source-address-range: the exporter range produced by row `network-derivation.representation` (the FABRIC leg, Pipeline 1) | (declared — r3 item 9: "the admitted sender is identified by its source address, which must lie in the exporter range of item 6") |
| observability-config.ingress.principal-unseen | the leg's own reads cannot confirm the enforcer sees the admitted attribute | gap · act-regardless | act-regardless; record the premise as UNTESTED in the package | (declared — r3 item 16: "the leg authors the change even when its own harvest cannot confirm the premise that the enforcer sees the admitted attribute on the path the exporter traffic takes; in that case it records the premise as UNTESTED in its package") |
| observability-config.ingress.granted-action | what the admitted principal may do | — | TCP 4317 and TCP 4318 only | (declared — r3 item 10: "the exporter range is authorised for TCP 4317 and TCP 4318 only") |
| observability-config.ingress.existing-grant | other allowances already on the same surface | replace · preserve · preserve-bounded | replace — the exporter range is the only permitted sender on these two ports; other listeners are untouched | (declared — r3 item 11: "the exporter range is the only permitted sender; any other sender allowance on those surfaces is replaced, not kept. Rules for other workloads, and for listeners other than the declared ingress, are not touched") |
| observability-config.ingress.target-empty | the declared ports carry no configuration | act · gap | gap — report what is absent and add no listener or configuration of its own | (declared — r3 item 12: "If the declared OTLP ingress carries no configuration for TCP 4317 and TCP 4318, the observability leg reports a gap naming what is absent and adds no listener or configuration of its own") |
| observability-config.ingress.enforcer-absent | no policy object governs the receiver yet | create · gap | for the declared-ports-absent condition, row `observability-config.ingress.target-empty` governs and reads **gap** — this supersedes the generic create default of r3 item 13 for this leg's specific condition | (declared — r3 item 12, as above); the generic default is (declared — r3 item 13: "where a leg's harvest finds no policy object governing its receiver, the leg creates one") |
| observability-config.ingress.target-absent | the declared target itself does not exist | gap · create-target | gap — report and create nothing | (declared — r3 item 14: "if a declared target does not exist - … the OTLP ingress - the leg reports a gap naming what is absent and creates nothing") |
| observability-config.ingress.collateral | what else changes because enforcement now applies | — | senders other than the exporter range lose access to TCP 4317/4318; other listeners are untouched; the leg states this effect in its package | (declared — r3 item 15: "On the OTLP ingress, senders other than the exporter range lose access to TCP 4317 and TCP 4318 and other listeners are untouched; the observability leg states that effect in its package") |
| observability-config.ingress.untouched | what in the leg's own file stays as it is | — | everything in `observability/nginx/otlp-ingress.conf` other than the sender allowance of the two listeners: the `listen`, `http2`, `grpc_pass`, `proxy_pass`, `proxy_*` and `client_max_body_size` lines and the comments stay exactly as the file gives them | (declared — owner 2026-11-24: "the ingress leg leaves its own file's directive untouched") |

### A leg that changes one setting — observability-config, collector leg (Pipeline 3) and operator leg (Pipeline 4)

| id | question | options | rule or named target | source |
|---|---|---|---|---|
| observability-config.collector.change | what the collector leg sets | — | on the `batch` processor: `send_batch_size: 8192` and `timeout: 5s`; no other key of that processor is added or changed, and nothing else in `observability/otelcol/config.yaml` changes (the receivers, `memory_limiter`, the exporter, the extensions, the telemetry block and the pipeline's processor order stay as the file gives them) | (declared — owner 2026-11-24: "set the batch processor to `send_batch_size: 8192` and `timeout: 5s`") |
| observability-config.collector.values-basis | the basis of the two values | — | both values are declared by the owner; the leg chooses no value and states that both were declared | (declared — owner 2026-11-24) |
| observability-config.collector.target-absent | the file declares no `batch` processor | gap · create-target | gap — report what is absent and add no processor | (declared — owner 2026-11-24: "collector.target-absent = gap") |
| observability-config.operator.change | what the operator leg sets | — | on the TCP 14318 listener: `client_max_body_size` from `16m` to `32m`; nothing else in `observability/nginx/operator-access.conf` changes (the `listen`, `allow`, `deny`, `proxy_pass`, `proxy_*` lines and the comments stay as the file gives them) | (declared — owner 2026-11-24: "raise `client_max_body_size` on the TCP 14318 listener from `16m` to `32m`") |
| observability-config.operator.value-basis | the basis of the value | — | `32m` is declared by the owner; the leg chooses no value and states that it was declared | (declared — owner 2026-11-24) |
| observability-config.operator.current-value | the listener's held file does not show `client_max_body_size 16m;` | gap · act | gap — report the line the held file shows (or its absence) and make no edit | (declared — owner 2026-11-24: "operator.current-value not 16m = report, no edit") |
| observability-config.operator.target-absent | the file declares no TCP 14318 listener | gap · create-target | gap — report what is absent and add no listener | (declared — owner 2026-11-24: "operator.target-absent = gap") |
| observability-config.collector-operator.consumes | does the collector or operator leg use the exporter range | — | no — neither consumes any value from another leg, and neither writes an address | (declared — owner 2026-11-24: "Consumes no exporter range") |

## Decisions needed from the owner

none — every design-decision row above is declared. (The `observability-config.ingress.enforcer-absent` row carries a note that r3 item 12's ingress-specific instruction takes precedence over item 13's general default — a documented precedence, not an unresolved question.)

## Why this is sequenced — the design rationale, read before questioning the DAG

**The test that decides sequenced vs parallel** — apply it explicitly and record the answer:

> Is every value the downstream domain needs **knowable before the upstream domain runs**?
>  - **Yes** ⇒ parallel; the values belong in the **interface contract**.
>  - **No** ⇒ sequenced; the value must ride a **DAG edge** (inter-pipeline chaining).

The exporter-range CIDR (row `network-derivation.representation`) is **not** knowable before the fabric leg runs: it is computed from the fabric devices' interfaces as the leg's own sources show them — which interfaces exist, which carry the exporter description marker, and what IPv4 addresses they hold. That changes whenever the fabric is reconfigured (an interface is added, removed, relabelled, or renumbered), and the addresses are regenerated whenever the lab is rebuilt. The Program Architect that builds the executable plan reads only `topology.json` and this document, so it structurally cannot know this value — it can only wire the DAG edge that lets the fabric leg's own execution produce it and hand it forward. **Only Pipeline 2 (ingress) needs it**, so only the fabric → ingress edge is sequenced.

Pipelines 3 (collector) and 4 (operator) need no value from any other leg: every value they use is declared above. By the same test they are **parallel** — with each other, with Pipeline 1 and with Pipeline 2 — and start after the program plan gate. Ordering them behind the fabric leg would assert a dependency the change does not have, and would let a failure in the fabric leg block two unrelated changes.

Guessing the CIDR up front (e.g. from a design-time assumption about the fabric's addressing scheme, or from a larger range a file's comment names) would risk authorising a range that is narrower than the exporter population (breaking legitimate telemetry export) or wider than it (granting access to addresses that were never marked as exporters) — exactly the drift this program exists to eliminate.

## Approvals — one gate per change leg, plus the value gate and the program plan gate

**Approvers are DECLARED, never chosen.** Every approver below is TRANSCRIBED from the approver mapping declared for this program, and marked `(declared)`.

- Program plan approver is Josh Allen, josh.allen@paichart.com (declared)
- Fabric exporter value approver is Steve Terry, steve.terry@paichart.com (declared)
- OTLP ingress change method approver is Jacob Wilcox, jacob.wilcox@paichart.com (declared)
- Collector change method approver is Jacob Wilcox, jacob.wilcox@paichart.com (declared)
- Operator listener change method approver is Jacob Wilcox, jacob.wilcox@paichart.com (declared)

Jacob Wilcox holding all three observability gates is intentional (declared — owner 2026-11-24).

### Every gate declares WHAT it approves and WHEN it sits

| gate | approves | moment — runs AFTER | blocks | approver |
|---|---|---|---|---|
| program plan | the plan and the interface contract | the Program Architect | every leg | Josh Allen, josh.allen@paichart.com (declared) |
| fabric exporter value | the value produced by the network-derivation (fabric) leg — the derived exporter-range CIDR | the fabric leg finishing its derivation | Pipeline 2 (ingress) only | Steve Terry, steve.terry@paichart.com (declared) |
| OTLP ingress change method | the change package produced by Pipeline 2 (ingress) | Pipeline 2 producing its change package | program completion — does not block the leg's own authoring | Jacob Wilcox, jacob.wilcox@paichart.com (declared) |
| collector change method | the change package produced by Pipeline 3 (collector) | Pipeline 3 producing its change package | program completion — does not block the leg's own authoring | Jacob Wilcox, jacob.wilcox@paichart.com (declared) |
| operator listener change method | the change package produced by Pipeline 4 (operator) | Pipeline 4 producing its change package | program completion — does not block the leg's own authoring | Jacob Wilcox, jacob.wilcox@paichart.com (declared) |

**Dependency consequence, spelled out for every edge:**
- Pipeline 2 (ingress) depends on **the fabric exporter value gate** **AND** on **the fabric leg** directly:
  `network-derivation (fabric) leg → fabric exporter value gate` AND `network-derivation (fabric) leg → ingress leg`. The fabric exporter value gate itself also depends on the fabric leg.

  ⚠️ **The direct edge is not redundant with the gate edge.** The fabric exporter value gate carries approval, not data — it produces no deliverable. The ingress leg's only path to receiving the derived CIDR is the direct chained-context edge from the fabric leg; the gate edge only decides *when* the ingress leg may start.
- Pipelines 3 (collector) and 4 (operator) depend on the program plan gate only — not on the fabric leg and not on the fabric exporter value gate.
- Each observability leg's own change-method gate depends on that **same leg's completion**, and blocks only program completion — not that leg's own authoring:
  `ingress leg → OTLP ingress change method gate`, `collector leg → collector change method gate`, `operator leg → operator listener change method gate`.
- Apply order (out of scope for this run, stated for the person applying): the three packages touch three different files and no package depends on another, so they may be applied in any order, each after its own gate.

## Pipeline 1 objective — exporter range (network-derivation, value)

- **A value leg.** Changes nothing. This leg changes no device configuration. It harvests, derives and publishes the exporter-range CIDR for Pipeline 2. It authors no configuration change on any device.

- Harvest every interface on ceos1 and ceos2, **read-only**, from the sources its Device sources block declares.
- Identify the subset of harvested interfaces whose description carries the exporter marker (row `network-derivation.population`); compute the smallest CIDR block, aligned to a valid prefix boundary, that contains every one of those interfaces' IPv4 addresses (row `network-derivation.representation`). A larger range named in a comment of a source is not an allocation and does not set the width: minimality does.
- **If the harvest returns no interfaces matching the exporter marker**: apply row `network-derivation.inputs-empty` — report a gap naming that no interface anywhere in the fabric's declared scope carries the marker, and name the marker text that was applied. Publish no derived range. Never substitute a broader population or a different marker.
- **The deliverable MUST publish, explicitly and prominently**: the exporter-range CIDR produced by this leg's own derivation (row `network-derivation.representation`), and the exact description-marker text this leg applied (row `network-derivation.population`) — named by rule and by producer (this leg), never by today's value alone. Pipeline 2 depends on what this leg PRODUCES at run time, not on what was read while authoring this document.
- **Validation (mechanical)**: re-run the same read-only interface harvest across the fabric's scope; re-apply the marker filter and the aligned-smallest-CIDR rule — expected: the published CIDR equals the recomputed value, every re-obtained exporter-marked address lies inside it, and no address that does not carry the marker lies inside it.

### ⚠️ If this leg DERIVES a value the downstream leg consumes

- **The computation is shown in the DESIGN.** The deliverable carries the input block (the set of marker-matched interfaces, by device and interface name) and the result block (the derived CIDR), plus re-runnable checks each followed by the literal text it prints — never a sentence stating the conclusion.
- **Minimality, or the equivalent tightest-correct property.** A result looser than the minimum is a **REJECTABLE defect even when it violates nothing else**, because it authorizes more than the requirement needs.
  *Earned: Run 15 shipped a `/30` where `/31` was minimal — mechanically clean, and a REJECT.*
- **Re-selection FIRST, escalation LAST.** If a candidate boundary fails alignment, that rules out *that candidate* — not the whole harvested set. Recompute against the next valid alignment. Escalate only after establishing that no correctly-aligned minimal cover exists at all, and name which alignments were tested.
  *Earned: Run 12 declared the pool too fragmented while a clean pair was free the whole time.*
- ⚠️ **Verify by arithmetic, never by eyeballing.** For CIDR aggregation: `10.0.0.1` and `10.0.0.2` are adjacent but do **not** summarize to a `/31` — they straddle a boundary, and their minimal cover is a `/30` that swallows a neighbouring address (`10.0.0.0`–`10.0.0.3`). A `/31` covers an **aligned** pair only (e.g. `10.0.0.2`/`10.0.0.3`). Verify prefix alignment arithmetically (address AND netmask == network address) for every candidate boundary before publishing — never by visual inspection of the addresses.
  *Earned: Runs 5 and 6 lost on this directly; Run 12 compounded it.*
- **Verify member-by-member** before publishing: every harvested exporter-marked address is inside the derived result, and no address that lacks the marker is.
- 🔴 **STATE THE NULL CASE, always.** Say what the correct outcome is when the harvest yields no marker-matched interfaces (row `network-derivation.inputs-empty`, above) — a named gap report, never a guessed range.
  *Earned: 2026-09-20 — an unstated null case led a downstream Author to import an unrelated range and author a policy permitting writes from switch loopback addresses.*
- 🔴 **RUN YOUR OWN RULE.** Apply the stated derivation rule literally, step by step, to the harvested inputs, and confirm the width and boundary of the result matches what the rule as stated actually produces — not just that the published value looks plausible.
  *Earned 2026-09-21: a stated rule and a published value silently diverged in width; the value was right, the stated method could not have produced it.*
- 🔴 **The machine check is a FLOOR, not the bar.** A clean mechanical containment result is **not** evidence the derivation is correct — the checker verifies containment, not that minimality and alignment were actually honoured. **Satisfy the requirement; do not target the checker.**

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Pipeline 2 objective — OTLP ingress sender restriction (observability-config, change) — depends on Pipeline 1

- Read the sources the Config sources block below declares, and nothing else. **The change is to `observability/nginx/otlp-ingress.conf` only** (label `obs-ingress.otlp-ingress.conf`), as an edit to the file the platform holds for that label. The leg holds the other two declared files because the block declares them, and makes no edit to either.
- **Preconditions — read during the Phase 0 harvest for this authoring run**: the declared OTLP ingress file (row `observability-config.ingress.target`) and its current sender configuration for TCP 4317 and TCP 4318, to establish what, if any, sender restriction is configured on those two ports.
- Author sender-restriction configuration on the declared ingress's TCP 4317 and TCP 4318 listeners, admitting only the exporter range — as chained from Pipeline 1 — for those two ports (rows `observability-config.ingress.admitted-principal`, `.granted-action`).
- **Admitted-principal premise** (`observability-config.ingress.admitted-principal`): the ingress must see the sender's true source address, unmodified, on the path the exporter traffic takes to the OTLP listeners — where this leg's own reads cannot confirm that, apply row `observability-config.ingress.principal-unseen`: author the change regardless and record the premise as UNTESTED in the package.
- **Existence assumption** (row-governed, not stated as today's fact): where this leg's own reads find the declared ports carry no configuration at all, apply row `observability-config.ingress.target-empty`/`.enforcer-absent` (report a gap naming what is absent, and add no listener or configuration of its own); where they find existing sender configuration on those ports, apply row `observability-config.ingress.existing-grant` (replace — the exporter range becomes the only permitted sender on those two ports; other listeners are untouched); where the declared OTLP ingress file itself does not exist, apply row `observability-config.ingress.target-absent` (report a gap, create nothing).
- It consumes the exporter-range CIDR **as chained** from the network-derivation (fabric) leg — it does **not** re-derive it, and is forbidden from recomputing it. Containment for that value is discharged **upstream** (Pipeline 1) and re-verified at the program tier (see *Acceptance*).
  - **If §6 does not carry it**: escalate. Do not guess, do not substitute, do not proceed.
- **Collateral effect** (row `observability-config.ingress.collateral`): senders other than the exporter range lose access to TCP 4317 and TCP 4318; other listeners are untouched. State this explicitly in the change package.
- 🔴 **`client_max_body_size` is not this leg's.** The TCP 4318 listener in `observability/nginx/otlp-ingress.conf` carries `client_max_body_size 16m;`; this leg leaves that line, and every other line row `observability-config.ingress.untouched` names, exactly as the file gives it. The body-size change of this program is Pipeline 4's, in another file.

The leg's task description carries this `## Config sources` block exactly. It is the ONE Config sources block of the observability-config protocol in this program: Pipelines 2, 3 and 4 each carry it, character for character, and each of the three legs reads and holds every file it declares.

```
## Config sources
obs-otelcol: git-file — service github-service ; paichart/paichart-configs/observability/otelcol/config.yaml
obs-otelcol: live-read — service observability-readonly
obs-ingress.otlp-ingress.conf: git-file — service github-service ; paichart/paichart-configs/observability/nginx/otlp-ingress.conf
obs-ingress.otlp-ingress.conf: live-read — service observability-readonly
obs-ingress.operator-access.conf: git-file — service github-service ; paichart/paichart-configs/observability/nginx/operator-access.conf
obs-ingress.operator-access.conf: live-read — service observability-readonly
```

## Pipeline 3 objective — collector batch processor (observability-config, change)

- Read the sources the Config sources block below declares, and nothing else. **The change is to `observability/otelcol/config.yaml` only** (label `obs-otelcol`), as an edit to the file the platform holds for that label. The leg holds the two nginx files because the block declares them, and makes no edit to either.
- **Preconditions — read during the Phase 0 harvest for this authoring run**: the declared collector file (row `observability-config.collector.target`): the `batch` processor's current keys, and the pipeline that lists it.
- Set the `batch` processor to `send_batch_size: 8192` and `timeout: 5s` (row `observability-config.collector.change`). Both values are declared (row `observability-config.collector.values-basis`): the leg states that, and offers no alternative values.
- **Existence assumption** (row-governed): where this leg's own reads find no `batch` processor declared in the file, apply row `observability-config.collector.target-absent`.
- It consumes no value from another leg and writes no address (row `observability-config.collector-operator.consumes`).
- Nothing else in `observability/otelcol/config.yaml` changes, and nothing in either nginx file. State in the package that the change is confined to the two keys of the one processor.

The leg's task description carries this `## Config sources` block exactly. It is the ONE Config sources block of the observability-config protocol in this program: Pipelines 2, 3 and 4 each carry it, character for character, and each of the three legs reads and holds every file it declares.

```
## Config sources
obs-otelcol: git-file — service github-service ; paichart/paichart-configs/observability/otelcol/config.yaml
obs-otelcol: live-read — service observability-readonly
obs-ingress.otlp-ingress.conf: git-file — service github-service ; paichart/paichart-configs/observability/nginx/otlp-ingress.conf
obs-ingress.otlp-ingress.conf: live-read — service observability-readonly
obs-ingress.operator-access.conf: git-file — service github-service ; paichart/paichart-configs/observability/nginx/operator-access.conf
obs-ingress.operator-access.conf: live-read — service observability-readonly
```

## Pipeline 4 objective — operator listener body size (observability-config, change)

- Read the sources the Config sources block below declares, and nothing else. **The change is to `observability/nginx/operator-access.conf` only** (label `obs-ingress.operator-access.conf`), as an edit to the file the platform holds for that label. The leg holds the other two declared files because the block declares them, and makes no edit to either.
- **Preconditions — read during the Phase 0 harvest for this authoring run**: the declared operator file (row `observability-config.operator.target`): the TCP 14318 listener and its `client_max_body_size` line.
- Raise `client_max_body_size` on the TCP 14318 listener from `16m` to `32m` (row `observability-config.operator.change`). The value is declared (row `observability-config.operator.value-basis`): the leg states that, and offers no alternative value.
- **Existence assumption** (row-governed): where this leg's own reads find a `client_max_body_size` line other than `16m` on that listener, or none, apply row `observability-config.operator.current-value`; where they find no TCP 14318 listener, apply row `observability-config.operator.target-absent`.
- 🔴 **Which `client_max_body_size`.** Two declared files carry `client_max_body_size 16m;`: `observability/nginx/operator-access.conf` (the TCP 14318 listener — this leg's) and `observability/nginx/otlp-ingress.conf` (the TCP 4318 listener — not this leg's, and not changed by any leg of this program). This leg edits the line in `observability/nginx/operator-access.conf` only; the line in `observability/nginx/otlp-ingress.conf` stays exactly as the file gives it.
- It consumes no value from another leg and writes no address (row `observability-config.collector-operator.consumes`). The listener's `allow` / `deny` lines are not a sender restriction of this program and stay as the file gives them.

The leg's task description carries this `## Config sources` block exactly. It is the ONE Config sources block of the observability-config protocol in this program: Pipelines 2, 3 and 4 each carry it, character for character, and each of the three legs reads and holds every file it declares.

```
## Config sources
obs-otelcol: git-file — service github-service ; paichart/paichart-configs/observability/otelcol/config.yaml
obs-otelcol: live-read — service observability-readonly
obs-ingress.otlp-ingress.conf: git-file — service github-service ; paichart/paichart-configs/observability/nginx/otlp-ingress.conf
obs-ingress.otlp-ingress.conf: live-read — service observability-readonly
obs-ingress.operator-access.conf: git-file — service github-service ; paichart/paichart-configs/observability/nginx/operator-access.conf
obs-ingress.operator-access.conf: live-read — service observability-readonly
```

## Design constraints — split across the contract and the DAG

**Static → the interface contract** (knowable up front, agreed before any leg runs):
- Ingress leg: target TCP 4317, TCP 4318 on the declared OTLP ingress, file `observability/nginx/otlp-ingress.conf`
- Collector leg: the `batch` processor in `observability/otelcol/config.yaml`; `send_batch_size: 8192`, `timeout: 5s`
- Operator leg: the TCP 14318 listener in `observability/nginx/operator-access.conf`; `client_max_body_size` `16m` → `32m`
- The one observability-config Config sources block, carried by Pipelines 2, 3 and 4 alike (each leg reads and holds every file it declares, and changes only its own)

**Runtime → the DAG edge** (not knowable up front — see *Why this is sequenced*):
- Exporter-range CIDR — produced by the network-derivation (fabric) leg, chained into Pipeline 2's §6 only, settled before Pipeline 2 starts.

## Acceptance

- Each change package must include deterministic validation with expected outputs (per *Writing rules* #1 and #2) and a rollback plan.
- **Apply is out-of-band and human-gated in every leg.** This program produces approved change packages only — never applied changes.

### Program integration reviewer (Node C) verifies, from structured facts:

1. **the consumed exporter-range CIDR the ingress leg (Pipeline 2) used exactly equals the CIDR the network-derivation (fabric) leg produced** — the chained value, not a guess, not a recomputation;
2. **containment** — every one of the fabric leg's own harvested exporter-marked addresses (as re-obtained by the fabric leg's own validation step) lies inside the published CIDR;
2b. **the tightest-correct property** — Node C recomputes the smallest aligned CIDR from the fabric leg's own published input set and confirms it equals the published value; a looser-than-minimal result is a REJECTABLE defect regardless of any other passing check;
3. **no-widening / no-collision** — the published CIDR is not a supernet broader than the minimal cover, and the ingress package grants only TCP 4317/4318 to that CIDR — nothing broader; no other package writes the range or any other address;
4. **chaining coverage** — the ingress leg received the network-derivation (fabric) leg's **real** deliverable, not a fallback and not nothing. The counters (`predecessors === chainCapablePredecessors`, `degradedPredecessors === 0`, `notChained []`) are **platform facts the program gate computes mechanically**; no reviewer tool exposes them, so Node C does not re-derive them and does not block for being unable to read them. Node C checks what its own chained context shows: the fabric leg appears as a predecessor to the ingress leg, carrying its `report.md` deliverable — not an upstream output marked as a fallback, and not missing. (Narrowed from four-domain r3: one consuming leg here, not three.)
5. **held files** — each observability change is made to the held file of its own leg's label; each leg's platform edit-application fact reads applied, and no other part of a held file changes.
6. **one file per leg** — the ingress package edits only `observability/nginx/otlp-ingress.conf`, the collector package only `observability/otelcol/config.yaml`, the operator package only `observability/nginx/operator-access.conf`; no package edits a file another leg owns.
7. **one body-size change** — only the operator package touches `client_max_body_size`, only in `observability/nginx/operator-access.conf`, from `16m` to `32m`; the `client_max_body_size` line of `observability/nginx/otlp-ingress.conf` is unchanged in every package.
8. **one processor change** — the collector package sets `send_batch_size: 8192` and `timeout: 5s` on the `batch` processor and changes no other key or line of `observability/otelcol/config.yaml`.

- 🔴 ⚠️ **THE CHECK NUMBERS ABOVE ARE FIXED. A NEW CLAUSE MAY NOT TAKE ONE.** They are referenced by number from elsewhere in this document and from the protocol; renumbering, merging, or substituting one **silently deletes it**. If a new requirement needs a number, it **APPENDS** (9, 10, ...).

- Note these checks are **properties, not hardcoded values** — they stay valid when the environment is rebuilt. That is deliberate: the round must not depend on a magic expected string.

- ⚠️ **Require evidence where its READER looks, not only where it is convenient to write.** Each observability leg's own deliverable must state, in its own package, the effect it produces (the sender-restriction effect for ingress; the two keys of one processor for the collector; the one directive of one listener for the operator) — a program-level statement alone is invisible to a check that reads legs.

### Consuming-leg attribution — the ingress leg cannot self-check the exporter-range CIDR

The ingress leg consumes the exporter-range CIDR as a chained value it is forbidden from recomputing, and cannot verify it against its own reads (it reads no fabric interface). The SATISFIED condition for its authorisation change package is: (1) the network-derivation (fabric) leg's own derivation was machine-checked with no defect (Pipeline 1's *Validation (mechanical)* step passed); (2) the program-tier checks 1–3 above pass on the chained value as received by the ingress leg; and (3) chaining coverage (check 4) confirms the ingress leg received the fabric leg's real deliverable. The collector and operator legs consume no value and need no such condition.

## Connection surfaces

The value leg reads the two switch files through the platform's Git file source, and the running switches through a
self-provisioned read-only MCP service registered from the descriptor URL its Device sources lines name (`topology.json`
`readOnlyServices.fabricDescriptorUrl`). Each observability leg reads the three observability files through the Git file source,
and the served copy of each through the read-only observability service registered on the install under the name
`observability-readonly` (`topology.json` `readOnlyServices.observabilityServiceName`), registered from the descriptor
https://raw.githubusercontent.com/paichart/paichart/main/descriptors/observability-readonly-descriptor.json (`readOnlyServices.observabilityDescriptorUrl`). That service is registered before the program is launched and its lines name it
by that name, never by a descriptor URL: a program with three observability legs that each registered the same descriptor would
delete each other's registration. No leg registers, updates or deletes it. `topology.json` declares no endpoint, category or
tools of its own.

## Open questions

none.

## Writing rules — read before authoring, they are the expensive part

*Rules version: 3 — 2026-09-25.* These govern how you write **every other section**. Every one was
earned by a failed or false-passing run.

1. ⚠️ **"Deterministic validation" means a reviewer can run it and compare, without judgement.**
   Every validation step is an **exact command** plus its **exact expected output** — the literal text
   or count you expect back. Prose like *"verify the loopback is up"*, *"confirm BGP advertises the
   aggregate"*, or *"check the policy is correct"* is a **REJECTABLE defect**, not a validation step:
   two reviewers could disagree on whether it passed.
   *Earned: Run 13's network leg was blocked for exactly this.*

2. ⚠️ **Ship every artefact your validation cites.** If a step invokes a policy/rule file (OPA,
   Conftest, tflint config, a test fixture), the change package must include that file's **complete,
   runnable contents**. Citing a check you did not ship is unrunnable, so it is not validation.
   *Earned: Run 10 was blocked for naming OPA/Conftest checks without shipping the rule files.*

3. 🔴 **State what must be TRUE. Do NOT name the measure that reports it.**
   Where a requirement can be written as a **property**, write the property — not the stamp shape, not
   the reason code, not the violation class, not `violations: []`. The **Program Architect** reads this
   file and composes every brief from it, so a machine pass-condition written here propagates into
   prompts **nobody inspects**, and becomes **a target an agent can aim at instead of the
   requirement**. Let the platform own the string.
   *Mechanism corrected 2026-09-21; the OBLIGATION is unchanged. This said "every agent reads this
   file". Measured: 0 of 197 change-package-author legs ever received this document, and the
   Architect is the only verbatim reader (66 of 92 executions). The hazard is WORSE than originally
   stated — the string reaches agents as a paraphrase nobody reviews.*
   *Earned: Run 15 (2026-07-29) — a leg met a published pass condition that was weaker than the
   requirement beside it, and shipped a defect. Declaring such a string "reference data" limits the
   damage; omitting it removes the temptation.*
   **Naming a measure is justified only when that state is the SUBJECT of the clause** and cannot be
   identified without it — and then say plainly that it is a state a leg legitimately lands in, never
   a bar to clear.

4. ⚠️ **Expected values stated in this document are reference data, NEVER evidence.** Where this file
   names an expected state, it describes the round's *intent* so a human can read the run. It is not
   an observation, and restating it is not a check. A tier must retrieve the **actual** value and
   construct its own finding.
   *Earned: Run 15 — Node C asserted a field's expected value, quoting the requirements, for a field
   that was **absent from the artifact entirely**.*

5. **Write properties, not hardcoded values**, wherever the environment can be rebuilt. If the rig
   re-randomizes, a magic expected string makes the round fail for the wrong reason.

6. ⚠️ **State every existence assumption a leg's objective rests on — as a BRANCH, never as today's
   state.** If a target resource may be ABSENT (a security group not yet created, an object tracked
   under another address), say what the leg does in each case: *"if the leg's own harvest finds no
   policy on the bucket, create one — absence is the expected starting point, not an escalation; if
   it finds one, modify it."* An unstated existence assumption is resolved by the design at runtime as
   an ambiguity — it costs retry generations, or worse, a guessed reconciliation. **Never write which
   branch is true today** (*"no policy exists"*, *"CREATE is the expected outcome"*): that is an
   observation of the environment, it goes false the moment anyone applies the change, and a program
   carries it forward as fact.
   *Earned: FW-A3.2/A3.3 — the same leg entered the retry band both rounds on exactly this
   ambiguity; FW-A3.5 stated it and the leg ran clean first-pass (VT-18). Rewritten 2026-09-25: the
   earlier wording asked for today's state, and a generated spec's "no enforcement point exists"
   reached a program's BINDING interface contract after the environment had gained one.*

7. ⚠️ **A constraint that exists only by convention does not exist for the agents.** Agents can
   honor any constraint observable in harvested facts or written here — nothing else. If a value is
   forbidden by operating convention but legal against every harvested fact (a subnet's zero
   address, a reserved-by-habit range), write the constraint or accept the value.
   *Earned: FW-A3.3 selected a pool containing the /24 zero address — legal against the harvest,
   off-convention, and invisible to every tier because the convention was written nowhere (VT-18).*

8. ⚠️ **State the platform dialect for any protocol ABSENT from harvested state.** A config author
   writing a protocol the target does not yet run has no harvested stanzas to imitate — it falls
   back to the textbook dialect, which is often another vendor's, and a reviewer with the same
   corpus gap approves it. If the target platform's syntax for the new protocol differs from the
   textbook form, write the platform's tokens as reference data (rule 4 applies), or accept that
   the first apply adjudicates them and may archive the round.
   *Earned: IGP-T1 R1 (2026-08-23) — an Arista EOS package carried two IOS-isms
   (`is-type level-2-only`, `metric-style wide`); the leg reviewer approved; the operator's EOS
   config-session entry rejected both, and the round was archived at its first apply gate.*
   **Prefer a positive exemplar over a negative token rule.** "Command X does not exist on this
   platform" is an omission-rule, and a generator's training prior re-inserts high-frequency
   tokens past it. A complete platform-native exemplar stanza (verified live where an operator
   can) converts generation into TRANSCRIPTION. Keep the negative list too — it is what a
   reviewer, an operator, and the platform's lint can all grep.
   *Earned: IGP-T1 R3 — with the negative dialect rules binding in its prompt, the author
   re-emitted the exact banned token R1 died on; the round was archived at its quality gate.*

   🔴 **WRITE THE EXEMPLAR — BUT DO NOT RELY ON IT HOLDING.** This rule used to end "...converts
   generation into transcription, WHICH HOLDS". That claim is now FALSIFIED and the correction is
   the most useful thing on this page. On IGP-T1 R11 the exemplar was present, complete, and
   BINDING in the leg's interface contract, under an explicit instruction to transcribe it — and
   the author silently dropped two of its lines. Its reviewer, carrying the same completeness rule,
   approved the package at 86/100 with no blocking issues. The omitted line left the routing
   protocol INACTIVE while the config entered, committed and displayed cleanly.
   What caught it was `dialect-lint`, which does not read.

   ⚠️ **One correction to that account, measured afterwards and worth more than the account itself.**
   This page used to say four guards were in force — protocol rule, role guidance, the exemplar, the
   reviewer — and that *all four* were prose that a language model bypassed. Three of those were
   genuinely in the author's prompt. **The exemplar was not.** The contract was binding on the LEG,
   but it was never delivered to the leg's own child tasks: the author received a harness-written
   paraphrase of it in its brief, **missing 7 of the exemplar's 10 lines** — and the reviewer's brief
   was missing 9 of 10. Measured across every archived leg that carried a contract, the same hole was
   universal: **7 of 7 legs lossy, 0 of N children ever holding the contract.** So the author did not
   ignore a complete exemplar; it faithfully transcribed an incomplete one. That is a mechanical
   defect, and it has since been fixed — the contract is now inherited verbatim by every child on its
   own structured channel, and briefs are forbidden from restating it.
   **The transferable lesson is the one that cost us the misdiagnosis: before concluding that a model
   ignored a rule, verify the rule was IN ITS PROMPT.** "Binding" is a property of a document; being
   *present* is a property of a prompt, and the two drift apart silently. A guard you believe is in
   force and that is merely absent produces evidence indistinguishable from a guard that was
   disobeyed — and it argues for exactly the wrong fix (write the prose more forcefully) while the
   real defect is that nothing was delivered.
   The rest of the account stands, and so does the conclusion: the reviewer DID hold the complete
   rule and still approved, and `dialect-lint` — which does not read — is what caught it.
   **So the exemplar's real value is not that an agent obeys it — it is that it is the SPECIFICATION
   the platform's lint checks against.** Nobody ever wrote "this line is required"; the lint derives
   every required line by decomposing this block. A better exemplar therefore buys you a better
   mechanical check, which is the part that actually holds. Write it carefully for that reason.
   *Earned: IGP-T1 R11 (2026-08-25) — dialect-lint's first live run, catching what four prose
   guards and one LLM reviewer had all passed.*
   **COMPLETENESS is half the rule, and the half that hides.** A required line of the exemplar that
   is ABSENT is as defective as a wrong token, and more dangerous: the config enters, commits and
   displays cleanly while the thing it configures stays INACTIVE. State completeness as a property —
   "the shape must appear COMPLETE, every line, in order" — and name the mechanism, never the line a
   prior round dropped.
   *Earned: IGP-T1 R7 — an omitted line left the protocol disabled; the package was banned-token
   clean and approved at 90/100 by a reviewer checking only the absence direction.*

9. ⚠️ **A validation target the harvest cannot see does not license prose.** When rule 1 demands a
   literal expected output for state the read-only service has no getter for, the author has two
   deterministic paths and must take (and name) at least one: derive the literal expectation from
   declared topology facts (identities, counts, states that are static by design — excluding and
   naming the dynamic fields), and/or mandate an operator-captured pre-change baseline of the exact
   command with a post-change byte-diff of the static fields. State the gap; never fabricate the
   baseline, and never describe the check in prose.
   *Earned: IGP-T1 R1+R2 — the same unharvestable check was handled well by one author (topology
   literals + operator capture) and as prose by the next, whose reviewer correctly blocked it; the
   deterministic shape was never written anywhere, so craft variance decided the round.*

10. ⚠️ **A `[NEUTRALIZED-...]` sanitizer marker seen in CHAINED context is a platform view-layer
    annotation — it is not evidence the marker exists in the document itself.** The platform
    sanitizes text at the boundary where one agent's output is chained into another's context, so
    a reviewer's view can carry a neutralization marker that the at-rest deliverable does not.
    A reviewer must report a marker as an OBSERVATION (naming where it appeared), never as a
    blocking document defect; deliverable hygiene is verified against the at-rest artifact by the
    program tier and the human operator, who can read the document as stored.
    *Earned: IGP-T1 R5 — a clean package's "System IDs..." paragraph false-positived an injection
    pattern at the chaining boundary; the reviewer, seeing the marker in its view, blocked a
    document that contained no marker at rest. The round was archived on a defect that did not
    exist.*

11. ⚠️ **Every validation step must be SATISFIABLE under the phase's own constraints.** Before you
    write an expected output, ask: *can this pass, GIVEN what this phase is required to do?* A step
    whose expected output is precluded by the phase's own requirement makes a CORRECT change look
    failed — the operator then rolls back good work, or "fixes" it by violating the requirement.
    Where a property can be observed several ways, state the PROPERTY and name an observable the
    phase does not preclude.
    *Earned: IGP-T1 R9 — a step required one protocol's routes to appear in the routing table while
    the same phase required the OTHER protocol to stay preferred, which guarantees they never
    install. The same defect recurred in that round's parity criterion, which compared installed
    routes during deliberate coexistence and reported failure on a healthy fabric.*

12. 🔴 **Writing rule 3 governs EVERY channel an agent reads — not just this file.** Task
    descriptions, gate comments, and run notes are all agent-readable contract. Naming a prior
    round's specific defect token there lets the agent satisfy the POINTER instead of the PROPERTY,
    and a round that then passes evidences only "the agent avoided the line it was told about".
    Name the property, name the mechanism, cite the earning round for provenance — never the token.
    *Earned: a round was superseded before its plan gate for exactly this, and re-run clean, which
    is the only reason its result was usable as evidence.*

13. ⚠️ **A value the evidence source does not directly carry must be labelled DERIVED, and its
    basis named.** Where a criterion requires such a value, the value is still legitimate — DERIVE
    it, then say it is derived and name what it was derived from. Never silently promote a
    derivation to a quotation, and never assert a blanket "every value here is a direct quote from
    tool output" over a table that contains one. Do NOT "solve" this by dropping the field or by
    switching to a source that merely prints the word: derive, disclose, and let the reviewer judge
    the derivation.
    🔴 **Check THIS document first.** If a deliverable spec tells the author to present such a value
    "as retrieved output", the author is doing what it was told and the defect is here, not in the
    agent. A requirement that asks for a value its own named evidence source cannot supply is the
    same class of defect as rule 11's unsatisfiable step.
    *Earned: IGP-T1 R15 and R16 — a derived value presented as a literal quote from a source that
    structurally cannot carry it. Where the topology makes the derivation trivially correct, the
    answer is RIGHT and only its stated provenance is wrong, which is exactly the shape a reviewer
    skims past: R16's reviewer blocked it, R15's did not and it shipped. The requirement itself had
    said "as retrieved output".*

14. ⚠️ **A numbered acceptance check keeps its NUMBER for the life of the program family, even
    when its property is narrowed.** Rounds are compared against each other, and "check 2 passed" is
    only meaningful if check 2 is the same check it was last round. When a topology or scope change
    makes a check's original property unobservable, do not renumber, delete, or silently substitute:
    keep the number, narrow the property HONESTLY, and state in the check itself that it is narrower
    and what a pass now evidences. Renumbering makes every prior round's result uncitable;
    substituting silently makes them wrong — a pass gets reported as evidence of a property nobody
    checked.
    *Earned: Run 15 (fabric expansion) — a new clause was added to a requirements file and the
    reviewer renumbered it into the slot held by the minimality check, which it then never
    performed; a non-minimal result shipped as approved. **A renumbering silently deletes a
    check.** The narrowing half was earned on IGP-T1's 2-node topology, where a check written for a
    richer fabric could not express its original property and kept its number with the narrowing
    stated, so the round stayed comparable.*

15. 🔴 **A crossing VALUE always names its producer. "the PRODUCED range" is not one value — it is two.**
    Wherever this file names a value that crosses between legs, write *"the range produced by the
    FABRIC leg"*, never a bare *"the PRODUCED range"*. A bare participle has no subject, and the
    phrase that follows it usually attaches the value to the CONSUMER's artifact (*"the produced range
    **as an ingress source**"*), which then reads as the consuming leg's own output. **Two readings of
    one sentence produce two different DAGs**, and a planner picks one without telling you which —
    unless it happens to notice.
    *Earned 2026-09-17 (telemetry-export-four-domain): the Approvals table said "the PRODUCED range as
    an ingress source" while the sentence four lines below said each downstream pipeline waits on its
    own gate. Both readings were defensible on the text. The Program Architect DID notice, chose one,
    flagged it as an Open Question and asked for confirmation before plan approval — the plan gate was
    released without answering it, and all four change packages were produced with zero domain
    approvals. The gates held the RELEASE, so nothing shipped; but an intent gate that runs after the
    work is a record, not a control.*
    **General form: a noun phrase that omits its subject gets bound to whoever reads it.** Apply it to
    crossing values first, because those decide the graph.
    ⚠️ **Do not over-generalise this to every role-agnostic sentence.** On the same run a role-agnostic
    *"show the computation in the deliverable"* was suspected of misdirecting the change-package author
    into a clause-(f) violation, and **measured not to** — the platform writes per-role task
    descriptions, and that instruction reached the architect and the reviewer but never the author.
    Verify that a sentence actually propagates to the role you think it misled before rewriting it.

    ### ✅ VALIDATED END TO END 2026-09-18 — and the same rule covers SCOPE WORDS, not just values

    A second instance of this family was found, fixed and **proven** on a live campaign, so the rule
    is no longer reasoning from one case.

    **The defect**: acceptance check 3 of a firewall program said *"no **hop** widens the flow."*
    "Hop" reads naturally as the DEVICE (edge / DMZ / core). It was also true of every match list
    WITHIN a device — and on an edge doing source-NAT that is two lists, a security ACL and a
    NAT-match ACL. Three rounds of the same program authored that one list three different widths:
    `tcp <partner> any eq 443` (destination too wide, **not caught**), the correct
    `tcp <partner> host <app> eq 443`, and `ip <partner> any`. The program reviewer blocked the third.
    The requirement was meticulous about the NAT POOL's minimality and silent about the NAT MATCH
    list, so which reading an author took was left to chance.

    **The fix was one definition** — no new obligation, no new constraint:
    > *"**Hop" here means every match list that selects traffic at that hop, NOT just the device.** ...
    > the check is on what the configuration PERMITS, not on what happens to reach it. Every selecting
    > list at a hop carries the same destination and port bounds as that hop's tightest one.*

    **The outcome, measured**: the next round went from `programReleasable: false` to **true**. The
    definition propagated with no human repeating it — the Architect's plan carried it, the leg's brief
    stated it as a named clause, the author **self-checked against it by name**, a second author in a
    different domain cited the same clause, and the program reviewer that had refused the round before
    approved with no blocking issues. Leg scores rose 85→88 and 84→90.

    🔴 **So the rule generalises past values: any term the acceptance checks TURN ON must be defined
    where it is used.** A value needs its producer; a scope word needs its extent. The test is the
    same one — *can this phrase be read two ways that produce different work?* — and the cost of
    leaving it is not a wrong answer, it is a **coin flip across rounds**, which is worse because it
    looks like craft variance and gets remediated at the wrong layer.

    ⚠️ **The discriminator that tells you which layer**: RECURRENCE. The same contract producing
    different results across rounds, from different authors, is an under-specified requirement and
    belongs here. A single slip — a transposed multiplication, a mis-scoped validation step — is craft
    and belongs in a re-run or in role guidance. Encoding a craft slip's specific answer into a
    requirement buys a green that proves nothing; it teaches to the test.

---
