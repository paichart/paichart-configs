# terraform-archive-owner-tag

One Terraform change leg adds the tag `owner = "data-platform"` to the archive bucket `aws_s3_bucket.archive`, as an edit to
`terraform/archive.tf` in this repository.

**Variants:** `git-only/` reads only `terraform/archive.tf`; `git-live/` also reads the Terraform state of the `prod` workspace
through the read-only Terraform service, as evidence of what exists. The two `requirements.md` files differ only in their
Config sources block and "Connection surfaces" (CI checks it).

**What must be running:** `git-only/` needs nothing running beyond the hub. `git-live/` needs the lab Terraform workspace behind
the read-only Terraform service (descriptor URL in its `topology.json`). Both need terraform-iac 1.17.0 or later; from that
version a Terraform leg reads only what its `## Config sources` block declares.

**What this does not do:** pAIchart computes no drift for Terraform and runs no plan. The package carries a `Plan witness`: the
resource, the action and the one key the change sets, with the sentence that tells the person applying it to stop if the
team's CI plan (for example an Atlantis plan on the pull request) shows anything else. That plan is the check; pAIchart works
beside it and does not replace it.

**What success looks like:** the package holds one edit to `terraform/archive.tf` that adds the `owner` line and leaves `team`
and `tier` as the file gives them. Its Plan witness names `aws_s3_bucket.archive`, "update in place" and `tags.owner` only. On
`git-only/` the package says it was designed against the `.tf` file only. The program reports `programReleasable: true`.

**Released:** `git-only/` and `git-live/` on 2026-11-19 (`programReleasable: true` both times).
