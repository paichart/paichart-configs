# telemetry-export-net-k8s-r2

A network value leg works out the telemetry exporter range from the lab switches; a Kubernetes change leg adds a NetworkPolicy in
`trading` that admits only that range to the telemetry receiver, on TCP 4317 and 4318.

**Revision 2** of [`telemetry-export-net-k8s`](../telemetry-export-net-k8s/). The only change to the specification: Pipeline 1
takes the exporter addresses "from the sources its Device sources block declares" instead of "from the running switches", so
one text serves both variants. The first revision stays as its run's input.

**Variants:** `git-only/` reads only the files in this repository (Pipeline 1 the switch files, Pipeline 2
`k8s/sample-workloads.yaml`); `git-live/` also reads the running switches and the live cluster. The two `requirements.md` files
differ only in their Device sources and Config sources blocks and "Connection surfaces" (CI checks it).

**What must be running:** `git-only/` needs nothing running beyond the hub. `git-live/` needs the lab switches ceos1 and ceos2
behind the read-only switch service and the lab cluster behind the read-only Kubernetes service (both descriptor URLs in its
`topology.json`). Both need kubernetes-gitops 1.19.0 or later.

**What success looks like:** Pipeline 1 publishes one aligned prefix covering every exporter address on both switches (from
today's files and switches, `10.99.0.0/27`; the leg works it out, the spec does not state it). Pipeline 2's package adds one
NetworkPolicy document to `k8s/sample-workloads.yaml` admitting only that prefix. On `git-live/` the platform's drift fact reads
no differences between the file and the cluster; on `git-only/` it is not checked and the package says it is a Git-only run.
The program reports `programReleasable: true`.

**Not yet run.**
