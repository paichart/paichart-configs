# Record who owns the archive bucket, in the file the team keeps in Git

One domain, one leg, one file. It is deliberately small.

## What must happen

The archive bucket `acme-archive` (resource `aws_s3_bucket.archive`, workspace `prod`) carries two tags, `team` and `tier`. Add
a third: `owner = "data-platform"`. The change is an edit to the `tags` map of that resource in the configuration-repository
file `terraform/archive.tf`.

Nothing else changes: `team` and `tier` keep the values the file gives them, no other attribute of the bucket changes, and no
other resource or file is touched. This run applies nothing and runs no plan. A person applies the approved package through
the team's own plan-and-apply pipeline after the Terraform change gate.

The team's CI plan on the approved change is the check that the apply does what the package says and no more. This run does
not compare the file with the running infrastructure and reports no drift. If the team's plan shows any change the package
does not name, the apply stops.

## Why this is a program and not one pipeline

It is a program so the plan, the interface contract and the integration review run over a change to a file the platform
holds. The single leg is the whole change.

## Approval gates

The program plan gate sits first. A gate sits after Pipeline 1 for the Terraform change.

| gate | approves | runs after | blocks | approver |
|---|---|---|---|---|
| program plan | the plan, the leg types and the interface contract | the Program Architect | Pipeline 1 | Josh Allen, josh.allen@paichart.com |
| Terraform change | the change package Pipeline 1 produced | Pipeline 1 producing its change package | program completion only, not Pipeline 1's own work | Jacob Wilcox, jacob.wilcox@paichart.com |

## Pipeline 1 objective — archive bucket owner tag (terraform-iac, change)

Read the sources the Config sources block below declares, and nothing else. Add `owner = "data-platform"` to the `tags` map of
`aws_s3_bucket.archive` as an edit to the declared file — not a new file, and not the file written whole.

- **Target:** the `tags` map of `aws_s3_bucket.archive` in `terraform/archive.tf`. The key `owner` is not in the file today.
- **Must not change:** the `team` and `tier` tags, every other attribute of `aws_s3_bucket.archive`, and every other resource.
- **If the file already carries an `owner` tag** when the leg reads it: stop and report; do not overwrite it.
- **Known and to be left alone:** the `prod` workspace holds other resources, some with planted test values. They belong to
  other work. This leg does not read their files and changes none of them.

The leg's task description carries this `## Config sources` block exactly:

```
## Config sources
archive-tf: git-file — service github-service ; paichart/paichart-configs/terraform/archive.tf
```

## Node C — integration review (facts only)

Check numbering is FIXED and referenced by number elsewhere. A new requirement APPENDS (5, 6, …).

1. The package adds exactly one key, `owner = "data-platform"`, to the `tags` map of `aws_s3_bucket.archive`.
2. In the package's edit, `team` and `tier` keep the values the declared file gives them.
3. No other resource, and no other attribute of `aws_s3_bucket.archive`, is changed.
4. The change is an edit to the declared file `terraform/archive.tf`.

## Validation shape

Governed by the leg's own active protocol, not by this file. This document does not restate, weaken or override a protocol
clause.

## Connection surfaces

The leg reads only its configuration file, through the platform's Git file source. It reads no Terraform state and no
running infrastructure; its package says it is a Git-only run. `topology.json` declares no endpoint, category or tools of
its own.
