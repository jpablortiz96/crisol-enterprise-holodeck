# CRISOL Architecture Diagram

```mermaid
flowchart TB
    subgraph UX["User Experience - crisol-web / Next.js"]
        CC["Command Center"]
        WS["Workspace Setup"]
        SS["Scenario Studio"]
        ER["Evaluation Room"]
        RC["Results Center"]
        TR["Tools & Readiness"]
    end

    subgraph CORE["Core Platform - crisol-api / FastAPI"]
        STORE["Workspace Store"]
        LIB["Scenario Library"]
        NPC["Scenario-driven NPC Ensemble"]
        ORCH["Multi-agent Orchestration"]
        CONSEQ["Consequence Engine"]
        EXAM["Examiner / Competence Report"]
        COACH["Coach"]
        MAP["Manager Fragility Map"]
        REPLAY["Time-Travel Replay"]
        MCP["MCP Tool Surface"]
        ASSURE["Telemetry / Evaluation / Security Checks"]
    end

    subgraph AZURE["Microsoft / Azure"]
        WEB["Azure Container Apps<br/>crisol-web"]
        API["Azure Container Apps<br/>crisol-api"]
        ENV["Container Apps Environment<br/>crisol-env"]
        ACR["Azure Container Registry"]
        SEARCH["Azure AI Search<br/>crisol-knowledge"]
        FOUNDRY["Microsoft Foundry<br/>Project Endpoint + Model Deployment"]
        SPEECH["Azure Speech<br/>optional voice synthesis"]
        LOGS["Log Analytics"]
    end

    subgraph DATA["Data Boundaries"]
        SAN["Sanitized workspace data"]
        PACKS["Scenario packs"]
        DOCS["Knowledge documents"]
        RUNTIME["Runtime sessions / audio / telemetry<br/>ignored by Git"]
    end

    CC --> WEB
    WS --> WEB
    SS --> WEB
    ER --> WEB
    RC --> WEB
    TR --> WEB

    WEB --> API
    API --> STORE
    API --> LIB
    LIB --> ORCH
    STORE --> ORCH
    ORCH --> NPC
    ORCH --> CONSEQ
    CONSEQ --> EXAM
    EXAM --> COACH
    EXAM --> MAP
    ORCH --> REPLAY
    API --> MCP
    API --> ASSURE

    ENV --- WEB
    ENV --- API
    ACR --> WEB
    ACR --> API
    API --> SEARCH
    API --> FOUNDRY
    API -. when configured .-> SPEECH
    WEB --> LOGS
    API --> LOGS

    STORE --> SAN
    LIB --> PACKS
    SEARCH --> DOCS
    ORCH --> RUNTIME
    ASSURE --> RUNTIME
```

## Grounding modes

```mermaid
flowchart LR
    REQUEST["Grounding request"] --> SEARCH_CHECK{"Azure AI Search<br/>configured and working?"}
    SEARCH_CHECK -- No --> LOCAL["local-fallback<br/>sanitized cited knowledge"]
    SEARCH_CHECK -- Yes --> FOUNDRY_CHECK{"Foundry project endpoint<br/>and model configured?"}
    FOUNDRY_CHECK -- No --> SEARCH_MODE["live-azure-search"]
    FOUNDRY_CHECK -- Yes --> FOUNDRY_MODE["live-foundry-iq"]
```

`live-foundry-iq` is the active production status as of June 11, 2026. Azure
AI Search performs live grounded retrieval. Local fallback remains available
for offline development and service failure. Simulations do not modify
production systems.
