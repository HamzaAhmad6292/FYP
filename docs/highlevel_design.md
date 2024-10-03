```mermaid
graph TD
    A[Admin] -->|Configure & Integrate| B[CRM Integration Service]
    B <-->|Sync Data| C[(CRM Database)]
    
    D[Scheduled Task] -->|Trigger| E[Client Classification Service]
    E <-->|Fetch Data| C
    E -->|Classify| F[Potential Client List]
    
    G[AI Interaction Scheduler] -->|Select Clients| F
    G -->|Schedule| H{Interaction Channel}
    
    H -->|Voice| I[Voice AI Service]
    H -->|Text| J[Chatbot Service]
    H -->|Email| K[Email Service]
    
    I & J & K -->|Initiate Contact| L[Customer]
    
    L -->|Respond| M[Interaction Handler]
    M -->|Route| N[API Gateway]
    
    N --> O[Core Services]
    O -->|Update CRM| B
    O -->|Analyze Call| P[Call Analysis Service]
    O -->|Manage Order| Q[Order Management Service]
    O -->|Generate Report| R[Reporting Service]
    
    S[Human Agent] <-->|Handover/Assist| M
    
    T[External Systems] <--> O

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style L fill:#f9f,stroke:#333,stroke-width:2px
    style S fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
    style N fill:#bbf,stroke:#333,stroke-width:2px
