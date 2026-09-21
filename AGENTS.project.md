# Project-specific Codex instructions

## Project purpose

- Maintain a small, auditable image-asset repository with explicit provenance and rights information for every stored asset.

## Project-specific sources of truth

- `README.md`: repository purpose and operating contract.
- Project-owned asset manifest/validator when present: canonical metadata for tracked image assets.

## Project-specific invariants

- Do not add image binaries without traceable source/provenance and a documented right/license basis suitable for the intended repository use.
- Record a stable digest and basic file metadata in the repository-owned manifest before treating an asset as accepted.
- Do not commit secrets, private user content, caches, or unrelated generated files.
- Keep the repository purpose narrow; do not turn it into an application repository unless explicitly requested.

## Project verification

- Run the repository-owned asset/manifest validator when present.
- For contract-only changes, verify manifest/schema consistency and GitHub Actions when configured.
