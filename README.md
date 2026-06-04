# Papers

This repository contains the OA PDF downloader tool (Electron UI + Python backend).

## Overview

- Electron UI (modern) provides:
  - Import from `.docx` / `.xlsx` or paste references
  - Detailed log window
  - Progress + resumable runs
  - Optional proxy configuration

- Python backend provides:
  - Reference parsing + metadata lookup
  - OA PDF discovery and download
  - PDF validation
  - `results.xlsx` report generation

## Output layout

Default output root: `D:\Papers`

For each input file, output is written to:

- `D:\Papers\<input_name>\pdfs\...`
- `D:\Papers\<input_name>\results.xlsx`

## Development

### Prereqs

- Windows 11 x64
- Node.js (LTS recommended)
- Python 3.11+

### Structure

- `app/` Electron app
- `backend/` Python backend

### Run (dev)

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m oa_downloader --help
```

Frontend:

```bash
cd app
npm install
npm run dev
```
