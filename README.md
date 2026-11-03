# paichart-configs

Configuration files of record for [pAIchart](https://github.com/paichart/paichart) pipelines, and the use cases that run
against them. A pipeline reads a file here through pAIchart's GitHub file source, **keeps its exact bytes**, and the Author
changes it only by edits to that kept file. You receive a package with the edits, a rollback and the checks to run;
**nothing is applied to your systems — applying is your step.**

| Folder | Domain | What it holds |
|---|---|---|
| `k8s/` | kubernetes-gitops | workload manifests |
| `terraform/` | terraform-iac | the workspace `.tf` files |
| `network/` | network-provisioning | one rendered startup configuration per device, per topology (`base`, `igp-2node`, `igp-triangle`) |

## Using it

- **On a self-hosted pAIchart:** set `GIT_FILE_SOURCE_PIN=paichart/paichart-configs` in the hub's `.env` (or your own repo — this
  one is an example), then follow the self-host run sheet step 9c. The rules for the pin and its limits are in pAIchart's
  `docs/SELF-HOST-KEPT-FILES.md`.
- **Pipelines read `main`.** It is protected: changes land by pull request only.

## What is never in this repo

- Terraform state, plans or variables files (`.gitignore`).
- Credentials of any kind: no kubeconfig, inventory credentials, tokens or `.env` files. Device logins are provisioned out of band.

## Licence

Apache-2.0 — see `LICENSE`.
