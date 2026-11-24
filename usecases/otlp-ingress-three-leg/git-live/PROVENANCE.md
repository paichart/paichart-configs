# Provenance — otlp-ingress-three-leg

- **Built from** [`telemetry-export-held-r3`](../../telemetry-export-held-r3/) `git-live/` in this repository (2026-11-24, owner
  decisions of that date). r3 stays published and unchanged.
- **Kept from r3:** the network value leg (Pipeline 1: the marker rule, the smallest aligned range, its derivation cautions), the
  observability sender-restriction design-decision rows (now `observability-config.ingress.*`), the plan and value gate approvers,
  Node C checks 1–5 (check 4 narrowed to one consuming leg, as it says), the sequencing test, and the *Writing rules* section byte
  for byte.
- **Removed:** the Kubernetes and Terraform legs, their rows, gates, constants and open questions.
- **Changed:** the observability leg is split in three, each changing one file: the ingress leg (`observability/nginx/otlp-ingress.conf`,
  the only consumer of the range), the collector leg (`observability/otelcol/config.yaml`, the `batch` processor) and the operator
  leg (`observability/nginx/operator-access.conf`, `client_max_body_size` 16m → 32m). All three carry one shared `## Config sources`
  block naming the three files. One change gate per observability leg (Jacob Wilcox). Node C checks 6–8 appended. Leg headings carry
  `(protocol, type)` per `docs/WRITING-A-SPEC.md`; r3's header lines naming an authoring POV are dropped.
- **Declared by the owner 2026-11-24 (drafted as proposals, then accepted):** rows `observability-config.collector.target-absent`,
  `observability-config.operator.current-value` and `observability-config.operator.target-absent`; Node C check 8.
- **Variant:** `git-live/`. The value leg's Device sources add a `device-read` line per switch (as in `loopback-ceos2/git-live/`);
  each observability file adds a `live-read` line, its served copy read as evidence through the pre-registered service
  `observability-readonly` (named by registered name, never by URL, because three observability legs share it).
- **Not a program input.** A program reads `requirements.md` and `topology.json` only.
