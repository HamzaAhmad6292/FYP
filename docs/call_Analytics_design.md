```mermaid

graph TD
    A[Call Recording] -->|Audio File| B[Speech-to-Text Converter]
    B -->|Transcript| C[Text Preprocessor]
    C -->|Cleaned Text| D[Entity Extractor]
    C -->|Cleaned Text| E[Sentiment Analyzer]
    C -->|Cleaned Text| F[Intent Classifier]
    D & E & F -->|Extracted Info| G[Analysis Aggregator]
    G -->|Comprehensive Analysis| H[Insight Generator]
    H -->|Call Insights| I[Report Formatter]
    I -->|Formatted Report| J[CRM Updater]
    K[Admin Interface] -->|Configure Analysis Rules| G
    L[Machine Learning Model] -.->|Improve Analysis| D & E & F
    M[Quality Assurance Module] -->|Review| I

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px