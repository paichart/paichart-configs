# paichart-configs

Configuration files of record for [pAIchart](https://github.com/paichart/paichart) pipelines, and the use cases that run
against them. A pipeline reads a file here through pAIchart's GitHub file source, **keeps its exact bytes**, and the Author
changes it only by edits to that kept file. You receive a package with the edits, a rollback and the checks to run;
**nothing is applied to your systems — applying is your step.**

**Network is the current focus.** Every released use case here is a network program. Kubernetes, Terraform and observability
are pending: their folders are present, but none of their use cases has run from this repository yet.

| Folder | Domain | Status |
|---|---|---|
| `network/` | network-provisioning — one startup configuration per device, per topology (`base`, `igp-2node`, `igp-triangle`) | **in use** |
| `k8s/`, `terraform/` | Kubernetes, Terraform | pending |
| `usecases/` | program inputs (`requirements.md` + `topology.json`) and what each run proved | see [`usecases/README.md`](usecases/README.md) |

## Self-host quick start

You need a self-hosted pAIchart with an Anthropic API key (pAIchart's `docs/SELF-HOST-RUN-SHEET.md` up to step 9b). Then:

1. **A GitHub token.** GitHub → Settings → Developer settings → Fine-grained tokens → *Public repositories (read-only)*, no
   permissions. Paste it into `services/github-service/.env` in your pAIchart clone.
2. **The pin.** In the hub's `.env`, set `GIT_FILE_SOURCE_PIN=paichart/paichart-configs` (or your own repo — see below) and restart
   the hub. Agents can read only that repository, and only its `main` branch.
3. **Start and register the GitHub file source.**
   `docker compose -f docker-compose.self-host.yml --profile git up -d --build`, then `npm run seed:github-service` — it prints the
   repository agents may read. Full detail and checks: pAIchart run sheet **step 9c**.
4. **Run a use case** that needs nothing but Git — start with `usecases/loopback-ceos2/git-only/`. Create a project, a phase and a
   stage, then a `PIPELINE` task titled `… (protocol: pov-program)` whose description names the variant's two raw URLs (example in
   [`usecases/README.md`](usecases/README.md#running-one)); attach the *Pipeline Harness* template and run it. Replace the
   placeholder approvers (`…@example.com`) with people on your project's team first, or every gate falls to you as project owner.

### What each use case needs

| Variant | What must be running besides pAIchart and the GitHub file source |
|---|---|
| `git-only/` | nothing — the files in this repository are the whole input |
| `git-live/` | the switches themselves, behind a **read-only** device service you register with a descriptor (point the Device sources lines and `readOnlyServices` at your descriptor's URL) |
| `live/` | the same, and you apply each phase's package to the switches between gates |

## Use your own repository

Copy the layout (`network/<topology>/<device>-startup.cfg`, one file per device), protect `main`, and pin
`GIT_FILE_SOURCE_PIN=<your-org>/<your-repo>`. In a use case's `requirements.md`, change every Device sources line from
`paichart/paichart-configs/…` to your repository and path. A spec that names a repository other than the pinned one is refused at
its first read. To write a spec from scratch, copy the shape of a released use case.

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
