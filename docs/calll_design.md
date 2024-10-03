```mermaid

graph TD
    A[Incoming Call] -->|Audio Stream| B[Speech Recognition Module]
    C[Outgoing Call] -->|Initiate| D[Call Dialer]
    D -->|Connected| B
    B -->|Transcribed Text| E[Natural Language Processor]
    E <-->|Context/Intent| F[Dialogue Manager]
    F <-->|Retrieve/Update| G[(Knowledge Base)]
    F -->|Response Text| H[Response Generator]
    H -->|Generated Response| I[Text-to-Speech Engine]
    I -->|Audio Response| J[Voice Channel]
    K[Sentiment Analyzer] -->|Emotion/Tone| F
    L[Call Control] -->|Manage Call| J
    M[Admin Interface] -->|Update Scripts| G
    N[CRM Integration] <-->|Client Info| F

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style M fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
    style K fill:#bbf,stroke:#333,stroke-width:2px