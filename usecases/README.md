# Use cases

Each folder is a pAIchart **program** input — a `requirements` file and a `topology.json` — whose earlier revision produced a
**released** run (`programReleasable: true`: every leg approved and the program's integration reviewer approved). The configs they
change are the files of record in this repository.

| Use case | Domains | What it does | Released |
|---|---|---|---|
| [`telemetry-export-held`](telemetry-export-held/) | network (value), Kubernetes, Terraform, observability | derives the smallest range covering the fabric's telemetry exporters, then authorises exactly that range in a NetworkPolicy, a bucket policy and a collector config | 2026-10-31 (pov-program 2.2.1) |
| [`held-terraform-window-p1`](held-terraform-window-p1/) | Terraform | adds `prevent_destroy` to the application log bucket, as edits to `terraform/main.tf` | 2026-10-21 |
| [`held-network-window-p1`](held-network-window-p1/) | network (value + change) | gives each switch a new telemetry-exporter loopback on a free address, derived from the current configuration | 2026-10-27 |

**Awaiting a released run:** a Kubernetes-only PodDisruptionBudget case (its only run was refused by the integration reviewer on
an unconfirmed teardown — a platform-fact gap, not the change). Kubernetes is covered above by `telemetry-export-held`.

## Running one

Launch a program whose task description names the two design artifacts by their raw URLs, for example:

```
Design artifacts for the Program Architect (fetch ONLY these two URLs):
- topology-as-code: https://raw.githubusercontent.com/paichart/paichart-configs/main/usecases/held-terraform-window-p1/topology.json
- requirements: https://raw.githubusercontent.com/paichart/paichart-configs/main/usecases/held-terraform-window-p1/requirements.md
```

The hub must be allowed to read this repository: `GIT_FILE_SOURCE_PIN=paichart/paichart-configs` (self-host run sheet step 9c).
`telemetry-export-held` uses `requirements.program.md` as its requirements artifact. Live legs also need the read-only services the
topology names; without them a leg stops and says why.
