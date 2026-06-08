# Release Candidate Report

## Product Status

CRISOL is packaged as a release candidate for local evaluation and controlled Azure deployment. The product includes the War Room, Scenario Library, synchronized NPC room, branching consequence timeline, competence reporting, manager insights, MCP tools, replay projection, telemetry, security scanning, and release automation.

## Completed Capability Checklist

- [x] Sanitized five-pack Scenario Library.
- [x] Standard and live simulation paths.
- [x] Azure Speech with synchronized text fallback.
- [x] Branching timeline, severity, contract exposure, and revenue delta.
- [x] Cited Competence Score and coaching plan.
- [x] Aggregate Manager Fragility Map.
- [x] Six-tool MCP surface and Tool Preview.
- [x] Deterministic Time-Travel Replay.
- [x] Groundedness, citation, safety, voice, tool, replay, and language evaluation.
- [x] Allowlisted local telemetry.
- [x] Recording Mode for 16:9 capture.
- [x] Non-root backend container with health check.
- [x] Local reset and clean baseline seeding command.

## Validation Checklist

- [x] Phase 4 branching and scoring validation.
- [x] Phase 5 competence and manager validation.
- [x] Phase 7 streaming and speech validation.
- [x] Phase 8 MCP and replay validation.
- [x] Phase 9 product-platform validation.
- [x] Scenario importer validation.
- [x] Evaluation harness.
- [x] Secret and sensitive-data scanner.
- [x] Product-language scan.
- [x] Frontend production build.
- [ ] Docker runtime smoke test on a host with an active Docker daemon.

Run the consolidated check:

```powershell
cd backend
python -m app.validate_release
```

## Security Posture

- `.env` is ignored and excluded from container context.
- Repository examples use sanitized or synthetic training data.
- Generated sessions, audio, and telemetry are ignored.
- Telemetry stores allowlisted identifiers and metrics only.
- Scenario imports apply structural and sensitive-content validation.
- Release scanning checks credential formats, connection strings, private keys, tokens, contact data, payment-card patterns, and prohibited business-data phrases.
- Runtime actions do not connect to production control planes.

Automated scanning reduces risk but does not replace code review, dependency review, secret rotation procedures, or deployment policy enforcement.

## Known Limitations

- Scenario data is sanitized training data.
- Foundry IQ live knowledge-base retrieval requires Azure configuration.
- Fabric IQ live ontology integration depends on available target capacity.
- Work IQ remains synthetic or local unless connected to approved enterprise tenant signals.
- Time travel is a deterministic replay projection.
- Generated audio is a local runtime artifact.
- Competence and certification outputs are readiness signals, not employment or official certification decisions.

## Deployment Readiness

The FastAPI backend can run locally, in the supplied container, Azure Container Apps, or Azure App Service. The frontend requires a build-time public backend URL. Production deployment still requires managed secret configuration, identity and network controls, durable storage decisions, observability routing, dependency scanning, and target-environment smoke tests.

## Recommended Next Steps

1. Run the Docker smoke test with an active daemon.
2. Validate Azure Speech, Foundry IQ, Fabric IQ, and Work IQ boundaries in the target environment.
3. Capture release screenshots from a clean seeded baseline.
4. Run accessibility and cross-browser checks.
5. Add authenticated access and deployment-specific authorization before shared enterprise use.
6. Tag the verified release candidate after reviewing the final diff.

## Screenshot Checklist

- [ ] Recording Mode command header and Scenario Library.
- [ ] Azure Speech active status.
- [ ] Live NPC pressure and cited event rail.
- [ ] Branching timeline with severity and revenue delta.
- [ ] Competence Score and evidence.
- [ ] Manager Fragility Map.
- [ ] Time-Travel Replay comparison.
- [ ] MCP Tool Preview.
- [ ] Enterprise training boundary footer.

## Recording Checklist

- [ ] Reset and seed local state.
- [ ] Start backend and frontend.
- [ ] Use a 16:9 browser viewport.
- [ ] Enable Recording Mode.
- [ ] Confirm Azure Speech or clearly labeled text fallback.
- [ ] Select a Scenario Library item.
- [ ] Run the scenario.
- [ ] Play the live simulation.
- [ ] Show citations, revenue delta, and branching timeline.
- [ ] Show Competence Score and Manager Fragility Map.
- [ ] Create a Time-Travel Replay branch.
- [ ] Run the MCP Tool Preview.
- [ ] Confirm the training boundary footer is visible.
