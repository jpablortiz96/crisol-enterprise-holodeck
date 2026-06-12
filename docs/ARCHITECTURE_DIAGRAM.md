# CRISOL Architecture Diagrams

## System overview

```mermaid
%%{init: {"theme":"dark","themeVariables":{"background":"#03090d","primaryColor":"#071016","primaryTextColor":"#f4f8fa","primaryBorderColor":"#22d3ee","secondaryColor":"#0b1720","tertiaryColor":"#102832","lineColor":"#526974","clusterBkg":"#071016","clusterBorder":"#27414b"}}}%%
flowchart LR
    subgraph UX["User Experience"]
        USER["Program Owners<br/>Candidates<br/>Managers"]
        WEB["crisol-web App Shell<br/>Command · Configure · Author<br/>Evaluate · Review · Operate"]
        USER --> WEB
    end

    subgraph CORE["Core Platform - crisol-api"]
        API["FastAPI Product API"]
        STORE["Workspace Store"]
        LIB["Scenario Library"]
        ORCH["Multi-agent Orchestration"]
        PERSONA["Scenario-driven Personas"]
        GROUND["Grounding Layer"]
        CONSEQ["Consequence Engine"]
        EXAM["Examiner / Report"]
        COACH["Coach"]
        MAP["Manager Fragility Map"]
        REPLAY["Time-Travel Replay"]
        MCP["MCP Tool Surface"]
        ASSURE["Telemetry / Security / Validation"]

        API --> STORE & LIB
        STORE & LIB --> ORCH
        ORCH --> PERSONA & GROUND & CONSEQ & REPLAY & MCP
        CONSEQ --> EXAM
        EXAM --> COACH & MAP
        API --> ASSURE
    end

    subgraph MS["Microsoft Services"]
        SEARCH["Azure AI Search<br/>crisol-knowledge"]
        FOUNDRY["Microsoft Foundry<br/>Project + gpt-4o config"]
        SPEECH["Azure Speech<br/>optional"]
        LOGS["Log Analytics"]
    end

    WEB --> API
    GROUND --> SEARCH & FOUNDRY
    PERSONA -. voice when configured .-> SPEECH
    ASSURE --> LOGS
```

Source: [`diagrams/01-system-overview.mmd`](diagrams/01-system-overview.mmd)

## Evaluation runtime sequence

```mermaid
%%{init: {"theme":"dark","themeVariables":{"background":"#03090d","primaryColor":"#071016","primaryTextColor":"#f4f8fa","primaryBorderColor":"#22d3ee","lineColor":"#67e8f9","actorBkg":"#071016","actorBorder":"#22d3ee","actorTextColor":"#f4f8fa","signalColor":"#67e8f9","signalTextColor":"#dce7ec","labelBoxBkgColor":"#071016","labelTextColor":"#dce7ec","noteBkgColor":"#102832","noteTextColor":"#f4f8fa","noteBorderColor":"#34d399"}}}%%
sequenceDiagram
    actor User
    participant Web as crisol-web
    participant API as crisol-api
    participant Workspace as Workspace + Scenario
    participant Grounding as Grounding Layer
    participant Search as Azure AI Search
    participant Orchestrator as Orchestration + Personas
    participant Speech as Azure Speech
    participant Consequence as Consequence Engine
    participant Examiner as Examiner + Coach
    participant Results as Results + Replay + Manager Insight

    User->>Web: Select scenario and evaluated profile
    Web->>API: Run or stream evaluation
    API->>Workspace: Load workspace, scenario, profile, and knowledge references
    API->>Grounding: Request grounded evidence
    Grounding->>Search: Search crisol-knowledge
    Search-->>Grounding: Sanitized ranked evidence
    Grounding-->>API: Citations and grounding mode
    API->>Orchestrator: Activate scenario and personas
    Orchestrator->>Speech: Synthesize persona line when configured
    Speech-->>Orchestrator: Audio or text fallback
    Orchestrator-->>Web: Situation, personas, and decision options
    User->>Web: Make decision
    Web->>API: Submit decision
    API->>Consequence: Evaluate systems, severity, and exposure
    Consequence-->>Web: Consequence delta and timeline update
    API->>Examiner: Score decisions and cited evidence
    Examiner-->>Results: Competence report and coach plan
    Results-->>Web: Results Center data
    API->>Results: Enable replay and manager aggregation
```

Source: [`diagrams/02-runtime-sequence.mmd`](diagrams/02-runtime-sequence.mmd)

## Azure topology

```mermaid
%%{init: {"theme":"dark","themeVariables":{"background":"#03090d","primaryColor":"#071016","primaryTextColor":"#f4f8fa","primaryBorderColor":"#22d3ee","secondaryColor":"#0b1720","tertiaryColor":"#102832","lineColor":"#526974","clusterBkg":"#071016","clusterBorder":"#27414b"}}}%%
flowchart TB
    Internet["Public users"] --> Web["Azure Container App<br/>crisol-web : 3000"]
    Web --> API["Azure Container App<br/>crisol-api : 8000"]

    subgraph Environment["Azure Container Apps Environment - crisol-env"]
        Web
        API
    end

    ACR["Azure Container Registry"] --> Web
    ACR --> API
    API --> Search["Azure AI Search<br/>crisol-knowledge"]
    API --> Foundry["Microsoft Foundry Project<br/>gpt-4o configuration"]
    API -. optional credentials .-> Speech["Azure Speech"]
    Environment --> Logs["Log Analytics"]

    API -. failure fallback .-> Local["Local cited grounding<br/>Text-only personas"]
```

Source: [`diagrams/03-azure-topology.mmd`](diagrams/03-azure-topology.mmd)

## Grounding modes

```mermaid
%%{init: {"theme":"dark","themeVariables":{"background":"#03090d","primaryColor":"#071016","primaryTextColor":"#f4f8fa","primaryBorderColor":"#22d3ee","lineColor":"#526974"}}}%%
flowchart LR
    Request["Grounding request"] --> SearchCheck{"Azure AI Search<br/>configured and working?"}
    SearchCheck -- No --> Local["local-fallback"]
    SearchCheck -- Yes --> FoundryCheck{"Foundry project +<br/>model configured?"}
    FoundryCheck -- No --> SearchMode["live-azure-search"]
    FoundryCheck -- Yes --> FoundryMode["live-foundry-iq"]
```

The live production grounding status is `live-foundry-iq`. Azure AI Search
performs retrieval; local cited grounding remains the failure and offline
fallback.
