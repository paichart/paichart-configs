# Provenance — telemetry-export-held-r2

- **Copied from** [`telemetry-export-held`](../telemetry-export-held/) in this repository (2026-11-16). That revision stays
  published and unchanged; stored runs that name its URLs keep working. From kubernetes-gitops 1.19.0 its Kubernetes leg stops at
  Phase 0, because it declares no `## Config sources` block.
- **The only change:** Pipeline 2 (kubernetes-gitops) now carries a `## Config sources` block, identical in `requirements.md` and
  `requirements.program.md`: the config-repo file the change is made to (`git-file`, `k8s/sample-workloads.yaml`) and the live
  cluster as evidence (`live-read`, through the read-only Kubernetes service descriptor). `topology.json` and every other leg are
  byte-unchanged.
- **Not a program input.** A program reads `requirements*.md` and `topology.json` only.
