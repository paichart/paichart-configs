# telemetry-export-net-k8s

A network value leg works out the telemetry exporter range from the lab switches; a Kubernetes change leg adds a NetworkPolicy in
`trading` that admits only that range to the telemetry receiver, on TCP 4317 and 4318.

Written by hand from a short objective with the spec checklist (`docs/WRITING-A-SPEC.md` in `paichart/paichart`). The same use
case as [`telemetry-export-held-r2`](../telemetry-export-held-r2/), cut to two legs.

**Variant:** `git-live/`. Both legs read their configuration files from this repository and the running systems: Pipeline 1 the
two switches (`## Device sources`), Pipeline 2 the cluster (`## Config sources`).

**What must be running:** the lab switches ceos1 and ceos2 behind the read-only switch service, and the lab cluster behind the
read-only Kubernetes service (both descriptor URLs in `topology.json`). Needs kubernetes-gitops 1.19.0 or later.

**Placeholders:** none in the values. The approvers' addresses are the project's own; a run on another install uses its own team.

**What success looks like:** Pipeline 1 publishes one aligned prefix covering every exporter address on both switches (from
today's files and switches, `10.99.0.0/27`; the leg works it out, the spec does not state it). Pipeline 2's package adds one
NetworkPolicy document to `k8s/sample-workloads.yaml` admitting only that prefix, and the platform's drift fact reads no
differences between the file and the cluster. The program reports `programReleasable: true`.

**Not yet run.**
