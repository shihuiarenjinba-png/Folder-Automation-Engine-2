# Folder -2 QA and Microsoft Store release gates

**Not ready for Microsoft Store.** Every result here must be verified against this -2 repository's exact commit; old `folder-automation-engine` artifacts are not -2 packages.

## Current port
- Source: `shihuiarenjinba-png/folder-automation-engine` `853b47ce82d936a0a74a345153f90da40934527a`
- Target base commit: `f03cd0c4dd8f1c6f626c145c1a97ada860d8c9b4`
- Main/release: not used
- -2 **MSIX Store identity is UNKNOWN/HOLD**.
- This repo's workflow builds a QA_UNSIGNED **EXE only**. It never signs or packages an MSIX using a guessed old Identity.

## Automated gates
- Python 3.12 unit tests with zero external live services
- Native Windows packaged GUI entrypoint self-test (no live user file mutation)
- PowerShell build script syntax check, artifact upload required
- Explicit checks for untouched file on preview, no overwrite, symlink protection, incomplete download protection, folder picker guards, and explicit copy/move approval

## Manual Windows GUI gates (not yet passed)
- 1024x768 and 1280x720 including 125% and 150% Windows scaling
- JP/EN change and preservation of settings, safe copy/move preview, start/stop watcher
- Restart and reproducibility, error state for locked file / permission denied / folder missing
- A folder that contains partially downloaded files and a zero-byte ordinary file
- Installer/runtime compatibility and third-party licensing review

## Mandatory packaging/Store gates (HOLD)
1. Confirm new -2 product's Package Identity Name, Publisher, Store ID, PFN and Version **directly in Partner Center**.
2. Add a new Store manifest builder explicitly referencing only those verified values. Never reuse old `FolderAutomationEngine` Identity.
3. Build an unsigned -2 MSIX for QA, capture exact SHA-256, EXE fingerprint, pack/unpack checks and source SHA.
4. Validate Windows install/runtime, Store images and Store certification checks.
5. Store submission and publication require a separate explicit user approval.

No marketing claim of fully working Undo/Restore: it has **not** been implemented or safety verified.
