# Docker Smoke Test

Run these commands from the repository root.

## Build

```powershell
docker build -t crisol-backend ./backend
```

## Run

```powershell
docker run --rm -p 8000:8000 --env-file .env crisol-backend
```

The local `.env` file remains outside the image and outside source control. Azure Speech variables are optional; without them, the backend reports text fallback through `/voice/status`.

## Verify

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/scenarios
Invoke-RestMethod http://127.0.0.1:8000/voice/status
```

Expected health fields:

```json
{
  "status": "ok",
  "service": "crisol-backend",
  "phase": "10-release-candidate"
}
```

Generated sessions, audio, telemetry, virtual environments, and environment files are excluded from the image context. Runtime folders are created inside the container and owned by the non-root service user.

## Stop And Remove

For the foreground command, press `Ctrl+C`. Because the container uses `--rm`, Docker removes it after shutdown.

For a detached run:

```powershell
docker run -d --name crisol-backend-smoke -p 8000:8000 --env-file .env crisol-backend
docker stop crisol-backend-smoke
docker rm crisol-backend-smoke
```
