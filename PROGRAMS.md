# A- program registry — repository-first Bubbles

Parent migration: [QuantaPhi #2110](https://github.com/www-infinity4/QuantaPhi/issues/2110). Brain implementation: [#1907](https://github.com/www-infinity4/QuantaPhi/issues/1907). Owner direction: a button invokes a versioned program; the owner phone is optional, not the sole production server.

## Run the source locally or in repository CI
Requires Node 22 or newer. No npm packages, keys or hosted API needed for this routing module.

```sh
node --test test/program-router.test.mjs
node --input-type=module -e "import {routeProgram} from './program-router.mjs'; console.log(routeProgram('resonance.calculate'))"
```

`routeProgram(id)` accepts an exact allowlisted program ID and returns routing metadata, never execution authorization. The catalog is immutable. It takes no user prompts, secrets, URLs, shell strings or caller-supplied permissions. The next integration must use a reviewed static import or version-pinned build artifact, not dynamic evaluation or fetching arbitrary code.

| ID | Existing source | Execution boundary |
| --- | --- | --- |
| resonance.calculate | QuantaPhi pure resonance module; draft #2159 | User browser, deterministic calculation; UI deployment unverified |
| conversation.reply | QuantaPhi Bubbles gateway/tools | Private authenticated API and real model; independent host missing |
| repository.engineer | Moltnook signed repository runner | Existing owner OIDC, grant, lease and fence; only authorized repo engineering |
| repository.monitor | Moltnook existing maintenance workflow | Bounded allowed repository maintenance; no public workflow dispatch |

GitHub Actions is for permitted repository engineering, not an always-on public chat server. Keep private prompts, tokens, wallet records and user replies out of GitHub. Actual execution must be recorded by the existing executor, never inferred from this catalog. Preserve existing grants, user isolation, model choice, databases, recovery watchers and branch policy. No new charges or production cutover.

## Checkpoints

- Original A- README remains intact (source tree previously contained README only).
- QuantaPhi Android source tests: 45/45, exit 0. GitHub vault tests: 94/94, PR #2157 merged. Synthetic fixtures are not provider inference.
- Current gateway HTTP 429, exact throttling rule unresolved. Original AI binding exists in Cloudflare; real independent model host not verified.
- QuantaPhi #2158 architecture draft and #2159 local program pilot; keep actual deployment and phone-off acceptance separate.
- Next: verify exact source CI and preview asset loading, wire reviewed catalog into existing UI and signed router, identify authorized independent inference host. No second active writer before complete state export, old-writer fence and rollback readiness.
