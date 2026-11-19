# Provenance — telemetry-export-held-r3

- **Copied from** [`telemetry-export-held-r2`](../../telemetry-export-held-r2/) in this repository (2026-11-19). That revision stays
  published and unchanged; stored runs that name its URLs keep working. From terraform-iac 1.17.0 its Terraform leg stops before
  it reads anything, because it declares no `## Config sources` block.
- **The only change:** Pipeline 3 (terraform-iac), identical in `requirements.md` and `requirements.program.md`:
  1. It carries a `## Config sources` block: the config-repo file the change is made to (`git-file`, `terraform/main.tf`) and the
     `prod` Terraform state as evidence (`live-read`, through the read-only Terraform service descriptor).
  2. Its first three bullets say the leg reads only those declared sources, does not compare the file with the state and reports
     no drift, and that the team's CI plan is the check. The sentence asking the task description to name the file is gone: the
     block does that.
  `topology.json` and every other leg are byte-unchanged.
- **Not a program input.** A program reads `requirements*.md` and `topology.json` only.
