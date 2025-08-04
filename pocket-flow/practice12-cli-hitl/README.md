# 有向图 流程

```mermaid
flowchart TD
    a(GetTopic) -->|generate| c(GenerateJoke)
    a -->|exit| b(Exit)

    c --> d(GetFeedback)
    
    d -->|Approve| a
    d -->|Disapprove| c
```

