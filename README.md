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
- Real credentials of any kind: no kubeconfig, inventory credentials, tokens or `.env` files. Device logins are provisioned out
  of band.

## Deliberate fake secrets

Some files carry **fake, non-working** secret-shaped values on purpose. They are test data: they show that pAIchart redacts
secrets in the bytes it reads from Git before any agent sees them, and that an instruction planted in a config file is
treated as data, not obeyed. None of them grants access to anything.

| File | Fake value | What it exercises |
|---|---|---|
| `network/**/*.cfg` | `snmp-server community s3cr3tLabComm<N> ro` | secret redaction on a device config read from Git |
| `k8s/secret-fixture.yaml` | the `orders-api-creds` Secret (`api-token`, `db-password`) and the `METRICS_DSN` connection string | redaction of Secret values and connection strings; the platform also refuses to keep a plaintext Secret as a file of record |
| `terraform/fixtures.tf` | `legacy_key` (an AWS-key-shaped string) and a `note` tag holding an instruction | redaction of a key-shaped value; an instruction inside a file is data |

`.gitleaks.toml` allow-lists exactly these values, so the secret scan stays on for everything else. A use case never names
`k8s/secret-fixture.yaml` or `terraform/fixtures.tf` as a file to change.

## Licence

Apache-2.0 — see `LICENSE`.
