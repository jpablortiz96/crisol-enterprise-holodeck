# Workspace Packages

Workspace packages move a sanitized CRISOL configuration between local installations. A package contains workspace configuration, roles, skills, profiles, knowledge documents, and complete scenario packs.

Exports are written to the ignored `backend/.crisol_exports/` directory by default.

## Export

From `backend`:

```powershell
python -m app.workspace.package --export
```

To choose a file name inside the export directory:

```powershell
python -m app.workspace.package --export creator-operations.json
```

The command validates all records before writing JSON and prints the package path and item counts.

## Inspect

```powershell
python -m app.workspace.package --summary .crisol_exports/creator-operations.json
```

The summary includes workspace identity, classification, counts, and scenario IDs.

## Import

```powershell
python -m app.workspace.package --import .crisol_exports/creator-operations.json
```

Import validates the complete package before changing local state. A valid import resets generated workspace and runtime state, restores records through the normal storage validators, and keeps examples disabled.

Import replaces the active generated workspace. Export the current workspace first when it must be retained.

## Package Contract

Every package uses `sanitized-training` classification and contains:

```json
{
  "package_id": "WPK-...",
  "workspace": {},
  "roles": [],
  "skills": [],
  "profiles": [],
  "knowledge": [
    {
      "file_name": "support_policy.md",
      "content": "# Support Policy"
    }
  ],
  "scenarios": [],
  "exported_at": "2026-06-11T00:00:00Z",
  "data_classification": "sanitized-training"
}
```

Packages containing invalid identifiers, broken role or skill references, unsafe file names, malformed scenarios, or sensitive-data patterns are rejected.
