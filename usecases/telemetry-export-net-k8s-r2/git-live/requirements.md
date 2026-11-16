# Admit our telemetry exporters, and only them, to the telemetry receiver in the trading namespace

Two legs: a value worked out on the network, then a Kubernetes change that uses it.

## What must happen

The two lab switches, ceos1 and ceos2, export telemetry from loopback interfaces whose description contains
`telemetry-exporter`. The exporter range is the smallest single aligned IPv4 prefix that contains every one of those
exporter addresses on both switches. It is worked out at run time from the switches; nobody types it in.

In the Kubernetes cluster, one new NetworkPolicy in the namespace `trading` admits only the exporter range, on TCP 4317 and
TCP 4318, to the pods labelled `app.kubernetes.io/component: telemetry-receiver`. The policy is added as a new document to the
config-repo file `k8s/sample-workloads.yaml`.

Nothing else changes: nothing on either switch, and nothing else in the cluster or in `k8s/sample-workloads.yaml`. This run
applies nothing. A person applies the approved Kubernetes package after the Kubernetes change gate.

## Why this is a program and not one pipeline

The Kubernetes policy admits a range that only the switches can tell us. The range is worked out, checked and approved on its
own before any policy is written with it.

## Approval gates

The program plan gate sits first. An approval gate sits between the two legs: the exporter range is approved before Pipeline 2
uses it. A gate sits after Pipeline 2 for the Kubernetes change.

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg types and the interface contract | the Program Architect | both legs | Josh Allen, josh.allen@paichart.com |
| exporter range | the exporter range Pipeline 1 published | Pipeline 1 publishing the range | Pipeline 2 | Steve Terry, steve.terry@paichart.com |
| Kubernetes change | the change package Pipeline 2 produced | Pipeline 2 producing its change package | program completion only, not Pipeline 2's own work | Jacob Wilcox, jacob.wilcox@paichart.com |

## Pipeline 1 objective — exporter range (network-derivation, value)

Harvest ceos1 and ceos2 read-only from the sources its Device sources block declares. An exporter address is the IPv4 address
of a loopback interface whose description contains `telemetry-exporter`; no other address on either switch is an exporter
address. Pipeline 1 takes the exporter addresses from the sources its Device sources block declares. Pipeline 1 publishes, for Pipeline 2, the smallest
single IPv4 prefix, aligned to its prefix boundary, that contains every exporter address on both switches, and it publishes the
description text it matched and the exporter addresses it found, by switch and interface. Where neither switch carries an
exporter address, Pipeline 1 reports that and publishes no range. Pipeline 1 works out the range and nothing else.
Changes nothing.

The leg's task description carries this `## Device sources` block exactly:

```
## Device sources
ceos1: git-file — service github-service ; paichart/paichart-configs/network/base/ceos1-startup.cfg
ceos1: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
ceos2: git-file — service github-service ; paichart/paichart-configs/network/base/ceos2-startup.cfg
ceos2: device-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/ceos-lab-readonly-descriptor.json
```

## Pipeline 2 objective — exporter policy in trading (kubernetes-gitops, change) — depends on Pipeline 1

Pipeline 2 adds one NetworkPolicy to the namespace `trading`, as a new document in `k8s/sample-workloads.yaml`. The policy
selects the pods labelled `app.kubernetes.io/component: telemetry-receiver`, and admits ingress only from the exporter range
Pipeline 1 published, on TCP 4317 and TCP 4318. Pipeline 2 uses that range and does not work it out again.

The exporters' traffic reaches the receiver pods directly, with no address translation, so the policy tells senders apart by
their source address. Pipeline 2 cannot confirm from its own reads that the receiver sees the exporters' own addresses; it
authors the policy regardless and records that premise as untested in its package.

The policy is the only rule that admits senders to the receiver pods: Pipeline 2 adds no other allowance on them. No pod carries
the receiver label today; Pipeline 2 authors the policy anyway, so it applies when receiver pods appear, and states the number
of matching pods it read, zero included. Once the policy selects the receiver pods, every other port and sender to them is
refused; this is intended, and the package states it. Allowances for other ports on those pods belong to the receiver workload's
own owner.

Pipeline 2 makes no other edit to `k8s/sample-workloads.yaml` and no other change in the cluster. The file and the live cluster
are known to agree; there is no difference between them that this program must leave alone. Never applied by this run.

The leg's task description carries this `## Config sources` block exactly:

```
## Config sources
sample-workloads: git-file — service github-service ; paichart/paichart-configs/k8s/sample-workloads.yaml
cluster: live-read — service https://raw.githubusercontent.com/paichart/paichart/main/descriptors/k8s-readonly-descriptor.json
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (3, 4, …).

1. The NetworkPolicy Pipeline 2 authored admits exactly the range Pipeline 1 published, and no other source.
2. The policy is in the namespace `trading`, selects the pods labelled `app.kubernetes.io/component: telemetry-receiver`, and
   admits TCP 4317 and TCP 4318 only.
3. Pipeline 2's change to `k8s/sample-workloads.yaml` is one new document, and no other line of the file changes.
4. The range Pipeline 1 published is one aligned IPv4 prefix that contains every exporter address Pipeline 1 listed, and no
   narrower aligned prefix contains them all.

## Validation shape

Governed by each leg's own active protocol, not by this file. This document does not restate, weaken or override a
protocol clause.

## Connection surfaces

Both legs read their configuration files through the platform's Git file source. Pipeline 1 reaches the running switches, and
Pipeline 2 the live cluster, only through a self-provisioned read-only MCP service named by the descriptor URL in
`topology.json` `readOnlyServices`. `topology.json` declares no endpoint, category or tools of its own.
