# CRISOL Architecture

CRISOL separates business-level architecture from implementation-level detail
so each audience can reach the right depth quickly.

## Architecture documents

| Document | Audience | Purpose |
| --- | --- | --- |
| [Executive Architecture](ARCHITECTURE_EXECUTIVE.md) | Product, business, and executive readers | Explains how knowledge becomes simulations, evidence, and risk insight. |
| [Technical Architecture](ARCHITECTURE_TECHNICAL.md) | Engineers and technical reviewers | Documents components, data flow, runtime contracts, Azure boundaries, and fallback behavior. |
| [Architecture Diagrams](ARCHITECTURE_DIAGRAM.md) | All readers | Presents the system overview, evaluation lifecycle, Azure topology, and grounding modes. |

## Diagram sources

Editable Mermaid sources are stored under [`docs/diagrams/`](diagrams/):

- [`01-system-overview.mmd`](diagrams/01-system-overview.mmd)
- [`02-runtime-sequence.mmd`](diagrams/02-runtime-sequence.mmd)
- [`03-azure-topology.mmd`](diagrams/03-azure-topology.mmd)

Render them with Mermaid CLI:

```powershell
npx -y @mermaid-js/mermaid-cli `
  -i docs/diagrams/01-system-overview.mmd `
  -o docs/diagrams/01-system-overview.svg
```

Repeat for the other `.mmd` files.

Rendered SVG exports are committed beside the Mermaid sources:

- [`01-system-overview.svg`](diagrams/01-system-overview.svg)
- [`02-runtime-sequence.svg`](diagrams/02-runtime-sequence.svg)
- [`03-azure-topology.svg`](diagrams/03-azure-topology.svg)

## Verified production boundary

- Frontend and backend run on Azure Container Apps.
- Azure AI Search performs live retrieval over `crisol-knowledge`.
- The Microsoft Foundry project endpoint and `gpt-4o` deployment configuration
  are present.
- The grounding status endpoint reports `live-foundry-iq`.
- Azure Speech integration is implemented; the current production voice
  endpoint reports text-only fallback.
- Local grounding and voice fallback remain available.
- Simulations do not execute production-system changes.
