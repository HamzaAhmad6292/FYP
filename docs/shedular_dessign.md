```mermaid

graph TD
    A[(Potential Client Database)] -->|Fetch Clients| B[Client Selector]
    C[Interaction History] -->|Past Interactions| B
    B -->|Selected Clients| D[Channel Determiner]
    E[Client Preferences] -->|Preferred Channels| D
    D -->|Client-Channel Pairs| F[Time Slot Allocator]
    G[System Capacity] -->|Available Slots| F
    F -->|Scheduled Interactions| H[Task Generator]
    H -->|AI Tasks| I[Voice AI Service]
    H -->|AI Tasks| J[Chatbot Service]
    H -->|AI Tasks| K[Email Service]
    L[Conflict Resolver] -->|Resolve Overlaps| F
    M[Admin Interface] -->|Set Rules & Priorities| B
    M -->|Configure Channels| D
    M -->|Adjust Capacity| G

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style M fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px