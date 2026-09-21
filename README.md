# images

## Purpose and owner

This repository is the auditable image-asset catalog for `palladiumailab-collabmAILab` projects. It stores approved raster or vector image artifacts together with enough provenance to reproduce or review their origin.

Repository owner: `palladiumailab-collabmAILab` maintainers.

The repository is intentionally empty of image binaries today. An empty manifest is a valid, auditable starting state; every future image must be added through the contract below.

## Scope

- Image files stored under `assets/files/`.
- One canonical manifest at `assets/manifest.json`.
- Per-asset source, license, and provenance metadata.
- Automated validation for manifest completeness, hashes, duplicate content, file type, size, and secret leakage.

Non-goals: application source code, model weights, private credentials, arbitrary downloads, and unreviewed temporary exports.

## Adding an image

1. Put the image under `assets/files/`.
2. Add one manifest entry using the schema in [`docs/asset-contract.md`](docs/asset-contract.md), including the exact SHA-256 and byte size.
3. Record the source, license/rights basis, and provenance (for generated art, record the tool/model and relevant generation reference).
4. Run the validator:

   ```bash
   python tools/validate_assets.py
   python -m unittest discover -s tests -p "test_*.py"
   ```

Only supported image formats up to 25 MiB are accepted. Do not commit `.env` files, keys, archives, executables, or other non-image payloads. Use an approved external storage or Git LFS workflow for artifacts that do not fit this repository's direct-Git policy, and keep their immutable URL and SHA-256 in a reviewed manifest extension before introducing one.

## Contract and CI

The machine-readable contract is [`assets/manifest.json`](assets/manifest.json), with field definitions in [`docs/asset-contract.md`](docs/asset-contract.md). GitHub Actions runs the validator and its regression tests for every pull request and push to `main`.
