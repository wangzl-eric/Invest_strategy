# QC Lean

`qc_lean/` is an optional local QuantConnect Lean workspace.

It contains a mix of:

- Lean engine source or submodule content
- local .NET runtime files
- Lean-formatted market data
- generated result artifacts
- example algorithms and config

This directory should be treated as an isolated external integration, not as a core Python package in the repository.

If you later want a deeper cleanup, the likely direction is to move this under an `external/` area or into a separate repository and update scripts and notebooks accordingly.
