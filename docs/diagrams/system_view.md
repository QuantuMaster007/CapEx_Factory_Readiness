# System view (one-screen)

```mermaid
flowchart LR
  CAPEX[CapEx Plan vs Actuals] --> VAR[Variance and Forecast]
  LT[Lead Times and Deliveries] --> EXP[Expedite Burn]
  FAC[Readiness Tasks] --> CP[Critical Path]
  FAC --> BLK[Blockers]
  FAC --> RAG[Readiness Score (RAG)]
  CP --> EXEC[Weekly Exec Update]
  VAR --> EXEC
  EXP --> EXEC
  BLK --> EXEC
  RAG --> EXEC
```
