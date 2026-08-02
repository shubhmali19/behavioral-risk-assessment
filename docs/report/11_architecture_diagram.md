# 11. Architecture Diagram

Two diagrams describe the system. The first is a block diagram of the deployment and the data that crosses each boundary. The second is a sequence diagram of a single assessment request, which is the artefact that demonstrates the components actually cooperate.

Both are maintained as Mermaid source in `docs/report/11_architecture_diagram.md` and rendered to vector graphics during the build, so the figures printed here cannot drift from the description in the text. The source may also be pasted into any Mermaid-aware editor, or into draw.io via *Arrange → Insert → Advanced → Mermaid*, and exported as PNG or SVG for use elsewhere.

## 11.1 Deployment and Data Flow

```mermaid
flowchart TB
    subgraph client["Presentation Tier — Container: frontend"]
        UI["React 19 + TypeScript<br/>Vite · Tailwind · Recharts"]
        NGX["nginx<br/>static assets · SPA fallback · /api proxy"]
        UI --- NGX
    end

    subgraph app["Application Tier — Container: backend"]
        RT["Routers<br/>health · predict · assessment · analytics"]
        SC["Pydantic Schemas<br/>validation · response envelope"]
        SV["Services<br/>assessment_service · ml_service"]
        MW["Logging Middleware<br/>duration · audit write"]
        RT --> SC --> SV
        MW -.-> RT
    end

    subgraph ml["ML Module — mounted at /ml"]
        INF["inference.predict()"]
        ART["Artefacts<br/>risk_model.pkl<br/>label encoders<br/>feature_columns.json<br/>preprocessing_params.json"]
        SHP["SHAP TreeExplainer"]
        INF --> ART
        INF --> SHP
    end

    subgraph data["Data Tier — Container: db"]
        PG[("PostgreSQL 15<br/>users · assessments · predictions<br/>behavioral_scores · audit_logs")]
    end

    OFF["Offline pipeline<br/>generate_dataset.py → preprocess.py → train.py"]

    Browser(["User's Browser"]) -->|"HTTPS"| NGX
    NGX -->|"JSON over HTTP :8000"| RT
    SV -->|"in-process call"| INF
    INF -->|"label · probabilities · SHAP"| SV
    SV -->|"SQLAlchemy ORM"| PG
    MW -->|"audit row"| PG
    OFF -.->|"writes artefacts"| ART

    classDef tier fill:#f8f9fa,stroke:#495057,stroke-width:1px
    class client,app,ml,data tier
```

**Three details to check on the rendered figure.** The call from the service into the inference module is an in-process arrow, not a network arrow, because it is a Python function call within a single interpreter — Section 10.4 explains why that boundary was not made a service. The offline pipeline is drawn with a dashed edge, since it does not run at request time and only deposits artefacts; the artefact it deposits that matters most is `preprocessing_params.json`, which is what prevents the training and serving feature computations from diverging (Section 22.4). And the middleware writes to PostgreSQL along its own edge rather than through `assessment_service`, which is why the audit log survives a failed prediction.

## 11.2 Request Sequence for `POST /assessment`

```mermaid
sequenceDiagram
    autonumber
    actor U as User's Browser
    participant R as Router<br/>(assessment.py)
    participant S as assessment_service
    participant M as ml_service → inference
    participant D as PostgreSQL

    U->>R: POST /assessment (26 fields, JSON)
    R->>R: validate against AssessmentInput
    alt validation fails
        R-->>U: 422 + offending field
    else validation passes
        R->>S: create_assessment(input)
        S->>D: INSERT assessments (status="pending")
        D-->>S: assessment_id
        R->>M: predict(input_dict)
        M->>M: clip to training IQR bounds
        M->>M: derive 7 features (persisted constants)
        M->>M: encode ordinals + one-hot, align 48 cols
        M->>M: RandomForest.predict_proba
        M->>M: TreeExplainer → SHAP values
        M->>M: rule-based biases + recommendations
        alt prediction raises
            M-->>R: exception
            R->>S: mark_assessment_failed()
            S->>D: UPDATE status="failed"
            R-->>U: 500
        else prediction succeeds
            M-->>R: label, probabilities, SHAP, scores
            R->>S: save_prediction(assessment_id, result)
            S->>D: INSERT predictions (1 row)
            S->>D: INSERT behavioral_scores (3 rows)
            S->>D: UPDATE status="completed"
            R-->>U: 200 {success, assessment_id, data}
        end
    end
    Note over R,D: LoggingMiddleware writes an audit_logs row<br/>on every request, including failures
```

**Why the sequence is drawn this way.** The `assessments` row is inserted and committed *before* the model is invoked. That ordering is what makes the `failed` status meaningful: had both writes shared one transaction, a failed prediction would roll back the assessment and leave no evidence the attempt occurred. Section 20.4 argues the point.

The four steps inside the inference lifeline are drawn separately rather than collapsed into one call, because they are precisely the steps that were implemented twice and disagreed. Section 22.4 documents the five divergences.

## 11.3 Labelling Conventions

Should the diagrams be redrawn by hand for the report rather than rendered from source, the following should be preserved.

| Element | Convention |
|---|---|
| Container boundary | labelled with the Docker Compose service name |
| Solid edge | a runtime path exercised by a live request |
| Dashed edge | an offline dependency; no request traverses it |
| Cylinder | a persistent store |
| Edge label | what crosses the boundary, not how |
| In-process call | drawn without a protocol label, to distinguish it from HTTP |

The last convention matters. A reader who sees an unlabelled arrow between the service and the ML module should understand that no serialisation, no network hop and no schema translation occurs there — which is the design decision Section 20.1 defends, and the reason a Spring Boot backend was not used.

---

> **Figure 11.1** — *Deployment and data-flow architecture.* Rendered from the source in §11.1. Solid edges are runtime paths; the dashed edge is an offline artefact dependency.

> **Figure 11.2** — *Sequence diagram for `POST /assessment`.* Rendered from the source in §11.2. Referenced as Figure 10.1 from Section 10.6 and as Figure 18.1 from Section 18; it appears once here and is cross-referenced from both. It is the single strongest piece of evidence that the system functions end to end, and should be reproduced at full column width.
