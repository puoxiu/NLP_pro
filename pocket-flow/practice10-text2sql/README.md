
## 节点 有向图

```mermaid
flowchart TD
    GetSchema --> GenerateSQL
    GenerateSQL --> ExecSQL
    
    ExecSQL -->|success| FinalResult
    ExecSQL -->|failure| DebugSQL
    ExecSQL -->|Max Retries| End
    DebugSQL -->|Corrected SQL| ExecSQL
```