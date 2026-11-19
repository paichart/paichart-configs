# telemetry-export-held-r3

One value worked out on the network, used in three domains: a network value leg works out the telemetry exporter range; a
Kubernetes leg, a Terraform leg and an observability leg each admit only that range (a NetworkPolicy, a bucket policy, a sender
restriction on the OTLP ingress).

**Revision 3** of [`telemetry-export-held`](../telemetry-export-held/). The only change from
[revision 2](../telemetry-export-held-r2/): the Terraform leg declares its `## Config sources` (from terraform-iac 1.17.0 a
Terraform leg without the block stops), and its text no longer asks for a comparison of the file with the state. Details:
`git-live/PROVENANCE.md`.

**Variants:** `git-live/` only. There is no `git-only/` variant: the exporter addresses, the observability stack's running
configuration and the cluster's live state exist only in the running systems.

**What must be running:** the lab switches ceos1 and ceos2, the lab cluster, the lab Terraform workspace and the lab
observability stack, each behind its read-only service (descriptor URLs in `git-live/topology.json`). Needs kubernetes-gitops
1.19.0 and terraform-iac 1.17.0 or later.

**Not yet run.**
