# OA PDF Downloader (Electron) - Project Requirements

This document captures the agreed requirements as of 2026-06-04.

## Key behaviors

- Input: `.docx`, `.xlsx`, and pasted references.
- Output root: `D:\Papers`.
- Output layout: create a subfolder per input file name.
- `results.xlsx` lives inside the per-input folder.
- Download: serial + 1s delay + retry 3x + timeout 30s.
- De-dup: by DOI.
- Resume: read previous `results.xlsx`, skip already-successful downloads.
- OA: search multiple OA sources; if not found, output official/DOI landing link.
- Validate downloads: content-type + PDF magic header `%PDF`.
- Proxy: optional, configurable in UI.
- Matching: strict title/author/year match when DOI is missing; no hard confidence threshold (best-effort automatic).
- Mixed Chinese/English references: supported.
- GUI: modern; implemented in Electron.
- Delivery: green (portable) build.

## Non-goals

- No paywalled downloads (only OA sources).
