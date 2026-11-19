# Provenance — held-terraform-window-p1

- **Copied from** `paichart/paichart` `program-artifacts/held-terraform-window-p1/` at commit `cfa8241` (2026-11-03). That copy stays published and
  unchanged; stored runs that name its URLs keep working.
- **The only change:** the config-repo references now name **`paichart/paichart-configs`** (this repository) instead of the
  private lab repository the original runs read. The files they name are the same files, mirrored here.
- **Not a program input.** A program reads `requirements*.md` and `topology.json` only.
- **Superseded (2026-11-19).** From terraform-iac 1.17.0 a Terraform leg reads only what a `## Config sources` block declares, and
  this specification has none, so its leg stops before it reads anything. It stays here as its earlier runs' input. For a Terraform
  change that runs today, see [`terraform-archive-owner-tag`](../terraform-archive-owner-tag/).

